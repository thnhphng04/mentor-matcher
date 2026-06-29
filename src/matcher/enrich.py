"""Turn messy bilingual (VI/EN) free text into structured tags.

Two enrichment paths share one cache schema on disk:

* **LLM** (OpenAI Structured Outputs) — higher quality; ``enrich_sync`` runs the
  interactive/in-app concurrent path, ``enrich_batch`` runs the cheap offline
  Batch-API pass.
* **Keyword/regex fallback** — fully deterministic VI/EN lexicon tagger. It
  populates every field (not just gender) so the tool runs offline with no API
  key, and it is the safety net per row when an LLM call fails.

Cache files (JSON, keyed by id) live in ``data/cache``:
    students_enriched.json, mentors_enriched.json
Each record carries ``source`` in {"llm", "keyword"} for transparency.
"""
from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .config import Config
from .data_io import Mentor, Student

# --------------------------------------------------------------------------
# Closed tag vocabularies — both enrichment paths emit only these, so scoring
# is deterministic and bilingual text normalises to the same tags.
# --------------------------------------------------------------------------
FOCUS_TAGS = [
    "emotional-support", "time-management", "study-habits", "life-skills",
    "accountability", "motivation", "exam-prep", "confidence",
    "communication", "focus-attention", "career-orientation", "stress-management",
]
TRAIT_TAGS = [
    "friendly", "patient", "structured", "motivating", "empathetic",
    "disciplined", "encouraging", "detail-oriented", "calm", "energetic",
]
SYMPTOM_TAGS = [
    "anxiety", "procrastination", "low-motivation", "distraction",
    "low-confidence", "social-difficulty", "academic-pressure",
    "emotional-difficulty", "behavioral", "none",
]

# --------------------------------------------------------------------------
# Bilingual keyword lexicons (phrase substring -> tag). Lower-cased matching.
# --------------------------------------------------------------------------
FOCUS_LEXICON: Dict[str, List[str]] = {
    "emotional-support": ["cảm xúc", "emotion", "tâm lý", "feel", "open up", "mở lòng", "tinh thần"],
    "time-management": ["quản lý thời gian", "time management", "thời gian", "schedule", "deadline"],
    "study-habits": ["thói quen học", "study habit", "học tập", "studying", "bài tập", "homework", "academic"],
    "life-skills": ["kỹ năng sống", "life skill", "soft skill", "kỹ năng mềm"],
    "accountability": ["tự quản lý", "accountab", "trách nhiệm", "kỷ luật bản thân", "self-management"],
    "motivation": ["động lực", "motivat", "thay đổi", "improve", "tiến bộ", "progress"],
    "exam-prep": ["thi", "exam", "kiểm tra", "ôn tập", "test prep"],
    "confidence": ["tự tin", "confiden", "self-esteem"],
    "communication": ["giao tiếp", "communicat", "nói chuyện", "express"],
    "focus-attention": ["tập trung", "focus", "attention", "concentrat", "distract", "phone"],
    "career-orientation": ["định hướng", "career", "nghề nghiệp", "tương lai", "orientation"],
    "stress-management": ["căng thẳng", "stress", "áp lực", "pressure", "lo lắng", "anxious", "nervous"],
}
TRAIT_LEXICON: Dict[str, List[str]] = {
    "friendly": ["thân thiện", "friendly", "dễ nói chuyện", "approachable", "warm"],
    "patient": ["kiên nhẫn", "patient", "nhẹ nhàng"],
    "structured": ["tỉ mỉ", "structured", "detail", "tóm tắt", "concise", "có hệ thống", "organized"],
    "motivating": ["truyền cảm hứng", "motivat", "inspir", "khích lệ"],
    "empathetic": ["đồng cảm", "empath", "thấu hiểu", "understanding", "lắng nghe", "listen"],
    "disciplined": ["kỷ luật", "disciplin", "nghiêm"],
    "encouraging": ["động viên", "encourag", "supportive", "hỗ trợ"],
    "detail-oriented": ["chi tiết", "detail-oriented", "cụ thể", "thorough"],
    "calm": ["bình tĩnh", "calm", "điềm tĩnh", "patient"],
    "energetic": ["năng động", "energetic", "nhiệt tình", "enthusiastic"],
}
SYMPTOM_LEXICON: Dict[str, List[str]] = {
    "anxiety": ["lo lắng", "nervous", "anxious", "anxiety", "sợ", "afraid", "worried"],
    "procrastination": ["trì hoãn", "procrastinat", "delay", "lười", "putting off"],
    "low-motivation": ["thiếu động lực", "unmotivated", "low motivation", "chán", "disengaged"],
    "distraction": ["phân tâm", "distract", "phone", "điện thoại", "mất tập trung", "easily distracted"],
    "low-confidence": ["thiếu tự tin", "low confidence", "rụt rè", "shy", "self-esteem", "insecure"],
    "social-difficulty": ["khó kết bạn", "social", "bạn bè", "isolat", "withdrawn", "opening up"],
    "academic-pressure": ["áp lực học", "academic pressure", "điểm số", "grades", "falling behind", "slow to"],
    "emotional-difficulty": ["cảm xúc", "emotional", "buồn", "stress", "căng thẳng", "overwhelm"],
    "behavioral": ["hành vi", "behavior", "bướng", "disruptive", "defiant"],
}

GRADE_RE = re.compile(r"(?:grade|lớp|grades?)\s*(\d{1,2})", re.I)


def _match_tags(text: str, lexicon: Dict[str, List[str]]) -> List[str]:
    low = text.lower()
    return [tag for tag, kws in lexicon.items() if any(k in low for k in kws)]


def extract_requested_gender(text: str, self_gender: str) -> Optional[str]:
    """Parse the parent's requested mentor gender (the hard-constraint field).

    Handles 'cùng giới (Male)', '(Female)', 'prefers a Male mentor',
    'mentor nam/nữ', and bare 'cùng giới'/'same gender' (-> the student's gender).
    Returns 'Male'/'Female' or None when no preference is stated.
    """
    low = text.lower()
    has_male = bool(re.search(r"\(male\)|male mentor|mentor nam|nam mentor|a male\b", low))
    has_female = bool(re.search(r"\(female\)|female mentor|mentor nữ|nữ mentor|a female\b", low))
    if has_male and not has_female:
        return "Male"
    if has_female and not has_male:
        return "Female"
    if has_male and has_female:
        # Ambiguous explicit mention -> defer to same-gender cue if present.
        pass
    if re.search(r"cùng giới|same gender|same-gender", low):
        return self_gender if self_gender in ("Male", "Female") else None
    return None


# --------------------------------------------------------------------------
# Deterministic fallback enrichers (full records).
# --------------------------------------------------------------------------
def keyword_enrich_student(s: Student) -> dict:
    text = f"{s.expectation} {s.symptom}"
    focus = _match_tags(text, FOCUS_LEXICON) or ["study-habits"]
    traits = _match_tags(s.expectation, TRAIT_LEXICON)
    sym = _match_tags(s.symptom, SYMPTOM_LEXICON)
    return {
        "requested_mentor_gender": extract_requested_gender(s.expectation, s.gender),
        "desired_focus": focus,
        "desired_traits": traits,
        "symptom_category": sym[0] if sym else "none",
        "source": "keyword",
    }


def keyword_enrich_mentor(m: Mentor) -> dict:
    text = f"{m.personalites} {m.expectation}"
    traits = _match_tags(m.personalites, TRAIT_LEXICON) or ["friendly"]
    focus = _match_tags(text, FOCUS_LEXICON) or ["study-habits"]
    needs = _match_tags(m.expectation, FOCUS_LEXICON)
    grade = GRADE_RE.search(m.expectation)
    return {
        "personality_tags": traits,
        "offered_focus": focus,
        "preferred_student": {
            "grade_band": grade.group(0) if grade else None,
            "needs": needs,
        },
        "source": "keyword",
    }


# --------------------------------------------------------------------------
# OpenAI Structured Outputs schemas + prompts.
# --------------------------------------------------------------------------
def _student_schema() -> dict:
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "requested_mentor_gender": {"type": ["string", "null"], "enum": ["Male", "Female", None]},
            "desired_focus": {"type": "array", "items": {"type": "string", "enum": FOCUS_TAGS}},
            "desired_traits": {"type": "array", "items": {"type": "string", "enum": TRAIT_TAGS}},
            "symptom_category": {"type": "string", "enum": SYMPTOM_TAGS},
        },
        "required": ["requested_mentor_gender", "desired_focus", "desired_traits", "symptom_category"],
    }


def _mentor_schema() -> dict:
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "personality_tags": {"type": "array", "items": {"type": "string", "enum": TRAIT_TAGS}},
            "offered_focus": {"type": "array", "items": {"type": "string", "enum": FOCUS_TAGS}},
            "preferred_student": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "grade_band": {"type": ["string", "null"]},
                    "needs": {"type": "array", "items": {"type": "string", "enum": FOCUS_TAGS}},
                },
                "required": ["grade_band", "needs"],
            },
        },
        "required": ["personality_tags", "offered_focus", "preferred_student"],
    }


_STUDENT_SYS = (
    "You extract structured tags from a parent/student note about a teen mentee. "
    "The text mixes Vietnamese and English. Only use the allowed enum values. "
    "requested_mentor_gender is the gender the parent explicitly asks the MENTOR to be "
    "(it may differ from the student's own gender); use null if not stated."
)
_MENTOR_SYS = (
    "You extract structured tags describing a mentor from their personality and "
    "expectation notes (mixed Vietnamese/English). Only use the allowed enum values."
)


def _student_payload(s: Student) -> str:
    return f"gender={s.gender}\nexpectation={s.expectation}\nsymptom={s.symptom}"


def _mentor_payload(m: Mentor) -> str:
    return f"gender={m.gender}\npersonalites={m.personalites}\nexpectation={m.expectation}"


def _client(api_key: Optional[str]):
    from openai import OpenAI
    return OpenAI(api_key=api_key) if api_key else OpenAI()


def _one_llm_call(client, model: str, system: str, payload: str, schema: dict, name: str) -> dict:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": payload}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": name, "schema": schema, "strict": True}},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


def enrich_sync(items, kind: str, model: str, api_key: Optional[str],
                max_workers: int = 8, max_retries: int = 2,
                progress_cb: Optional[Callable[[int, int], None]] = None) -> Dict[str, dict]:
    """Concurrent synchronous enrichment (interactive / in-app path).

    Each row is attempted up to ``1 + max_retries`` times (short backoff between
    attempts); only after all attempts fail does it fall back to the keyword
    enricher, so one flaky row never sinks the run. ``kind`` is "student"/"mentor".
    """
    client = _client(api_key)
    if kind == "student":
        sys, payload_fn, schema = _STUDENT_SYS, _student_payload, _student_schema()
        fallback = keyword_enrich_student
    else:
        sys, payload_fn, schema = _MENTOR_SYS, _mentor_payload, _mentor_schema()
        fallback = keyword_enrich_mentor

    out: Dict[str, dict] = {}
    total = len(items)
    done = 0

    def work(it):
        for attempt in range(1 + max_retries):
            try:
                rec = _one_llm_call(client, model, sys, payload_fn(it), schema, kind)
                rec["source"] = "llm"
                return it.id, rec
            except Exception:
                if attempt < max_retries:
                    time.sleep(0.5 * (attempt + 1))  # 0.5s, 1.0s backoff
        rec = fallback(it)
        rec["llm_failed"] = True  # transparency: API exhausted retries for this row
        return it.id, rec

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(work, it) for it in items]
        for fut in as_completed(futures):
            cid, rec = fut.result()
            out[cid] = rec
            done += 1
            if progress_cb:
                progress_cb(done, total)
    return out


def enrich_batch(items, kind: str, model: str, api_key: Optional[str],
                 poll_seconds: int = 10, timeout_seconds: int = 24 * 3600) -> Dict[str, dict]:
    """Offline OpenAI Batch API pass (50% cheaper). Used by the CLI.

    Falls back to keyword enrichment for any request the batch didn't return.
    """
    client = _client(api_key)
    if kind == "student":
        sys, payload_fn, schema = _STUDENT_SYS, _student_payload, _student_schema()
        fallback = keyword_enrich_student
    else:
        sys, payload_fn, schema = _MENTOR_SYS, _mentor_payload, _mentor_schema()
        fallback = keyword_enrich_mentor

    lines = []
    for it in items:
        lines.append(json.dumps({
            "custom_id": it.id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [{"role": "system", "content": sys},
                             {"role": "user", "content": payload_fn(it)}],
                "response_format": {"type": "json_schema",
                                    "json_schema": {"name": kind, "schema": schema, "strict": True}},
                "temperature": 0,
            },
        }))
    import io
    buf = io.BytesIO("\n".join(lines).encode("utf-8"))
    buf.name = f"{kind}_batch.jsonl"
    up = client.files.create(file=buf, purpose="batch")
    batch = client.batches.create(input_file_id=up.id, endpoint="/v1/chat/completions",
                                  completion_window="24h")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        batch = client.batches.retrieve(batch.id)
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            break
        time.sleep(poll_seconds)

    out: Dict[str, dict] = {}
    if batch.status == "completed" and batch.output_file_id:
        content = client.files.content(batch.output_file_id).text
        for line in content.splitlines():
            row = json.loads(line)
            cid = row["custom_id"]
            try:
                body = row["response"]["body"]
                rec = json.loads(body["choices"][0]["message"]["content"])
                rec["source"] = "llm"
                out[cid] = rec
            except Exception:
                pass
    # Fill anything missing with the deterministic fallback.
    by_id = {it.id: it for it in items}
    for cid, it in by_id.items():
        if cid not in out:
            out[cid] = fallback(it)
    return out


# --------------------------------------------------------------------------
# Cache I/O + the high-level accessor used by the matcher.
# --------------------------------------------------------------------------
def _cache_file(cfg: Config, kind: str) -> Path:
    return cfg.cache_path / (f"{kind}s_enriched.json")


def load_cache(cfg: Config, kind: str) -> Dict[str, dict]:
    f = _cache_file(cfg, kind)
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {}


def save_cache(cfg: Config, kind: str, data: Dict[str, dict]) -> None:
    cfg.cache_path.mkdir(parents=True, exist_ok=True)
    _cache_file(cfg, kind).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_enrichment(students: List[Student], mentors: List[Mentor], cfg: Config
                   ) -> tuple[Dict[str, dict], Dict[str, dict]]:
    """Return (student_records, mentor_records).

    Uses the committed cache where present; any id missing from cache is filled
    with the deterministic keyword enricher (so the matcher always has tags,
    even with no API key and an empty cache).
    """
    scache = load_cache(cfg, "student")
    mcache = load_cache(cfg, "mentor")
    srecs = {s.id: scache.get(s.id) or keyword_enrich_student(s) for s in students}
    mrecs = {m.id: mcache.get(m.id) or keyword_enrich_mentor(m) for m in mentors}
    return srecs, mrecs


def build_keyword_cache(students: List[Student], mentors: List[Mentor], cfg: Config) -> None:
    """Generate a full committed cache deterministically (no API needed)."""
    save_cache(cfg, "student", {s.id: keyword_enrich_student(s) for s in students})
    save_cache(cfg, "mentor", {m.id: keyword_enrich_mentor(m) for m in mentors})
