"""Streamlit UI for the mentor-student matcher.

Layout: Data · Enrichment · Q1 · Q2 · Q3 · Q4. Each question is self-contained —
its own controls and a **Run** button that executes *that question's* method
(no live auto-recompute). Q1 = hard constraints only; Q2 adds parent-expectation
scoring; Q3 adds two-way fit; Q4 simulates rejection and re-matches on Q3.
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

# Make `matcher` importable whether or not the package is installed.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Load a local .env (OPENAI_API_KEY / SUPABASE_*) if present.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import pandas as pd
import streamlit as st

from matcher import enrich as enrich_mod
from matcher import store as store_mod
from matcher.config import Config, Overrides, Pair, Thresholds, Weights, load_config
from matcher.data_io import (MENTOR_COLUMNS, STUDENT_COLUMNS, mentors_from_df,
                             students_from_df, validate_columns, ROOT)
from matcher.matcher import run_matching
from matcher.metrics import baseline_delta, summarize
from matcher.rematch import simulate_and_rematch

st.set_page_config(page_title="TeenCare Mentor Matcher", layout="wide")

# Bridge Streamlit secrets -> env so the non-Streamlit modules see them.
for _k in ("OPENAI_API_KEY", "OPENAI_MODEL", "SUPABASE_URL", "SUPABASE_KEY"):
    try:
        if _k not in os.environ and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
    except Exception:
        pass

file_cfg = load_config()
DEFAULT_STUDENTS = ROOT / "data" / "students_prod_2000_enriched.csv"
DEFAULT_MENTORS = ROOT / "data" / "mentors_prod_200_enriched.csv"


# --------------------------- dataset / enrichment state -------------------
def _rebuild_enrichment():
    sr, mr = enrich_mod.get_enrichment(
        st.session_state.students, st.session_state.mentors, file_cfg)
    st.session_state.srecs, st.session_state.mrecs = sr, mr


def set_dataset(students, mentors, sdf, mdf, source):
    st.session_state.students = students
    st.session_state.mentors = mentors
    st.session_state.students_df = sdf
    st.session_state.mentors_df = mdf
    st.session_state.data_source = source
    _rebuild_enrichment()


def _records(df):
    """DataFrame -> list of JSON-safe row dicts (NaN -> None) for Supabase."""
    return df.where(pd.notna(df), None).to_dict("records")


def load_default_dataset(persist: bool = False):
    sdf, mdf = pd.read_csv(DEFAULT_STUDENTS), pd.read_csv(DEFAULT_MENTORS)
    if persist:  # used by Reset: clear the DB so default is the source again
        store_mod.dataset_replace("student", [])
        store_mod.dataset_replace("mentor", [])
    set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf, "default")


def load_initial_dataset():
    """Prefer the dataset stored in Supabase; fall back to the bundled CSVs."""
    s_rows = store_mod.dataset_load("student")
    m_rows = store_mod.dataset_load("mentor")
    if s_rows and m_rows:
        sdf, mdf = pd.DataFrame(s_rows), pd.DataFrame(m_rows)
        set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf, "supabase")
    else:
        load_default_dataset()


if "students" not in st.session_state:
    load_initial_dataset()


def integrated_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


st.title("🎯 TeenCare Mentor–Student Matcher")
st.caption("Rule-driven, tunable matching · each question (Q1–Q4) runs its own method on **Run**")

# ----------------------------- sidebar: overrides -------------------------
sb = st.sidebar
sb.header("✍️ Overrides")
sb.caption("Search by name to add pairs. Applied when you click Run on any question.")

_student_label = {s.id: f"{s.name} · {s.id[:8]}" for s in st.session_state.students}
_mentor_label = {m.id: f"{m.name} · {m.id[:8]}" for m in st.session_state.mentors}
st.session_state.setdefault("force_pairs", [])
st.session_state.setdefault("block_pairs", [])


def _pair_editor(title, state_key, prefix):
    with sb.expander(title, expanded=False):
        s_sel = st.selectbox("Student", options=list(_student_label),
                             format_func=lambda i: _student_label[i], key=f"{prefix}_s")
        m_sel = st.selectbox("Mentor", options=list(_mentor_label),
                             format_func=lambda i: _mentor_label[i], key=f"{prefix}_m")
        if st.button("➕ Add pair", key=f"{prefix}_add", use_container_width=True):
            if (s_sel, m_sel) not in st.session_state[state_key]:
                st.session_state[state_key].append((s_sel, m_sel))
        for i, (a, b) in enumerate(st.session_state[state_key]):
            c = st.columns([5, 1])
            c[0].caption(f"{_student_label.get(a, a)} → {_mentor_label.get(b, b)}")
            if c[1].button("❌", key=f"{prefix}_rm{i}"):
                st.session_state[state_key].pop(i)
                st.rerun()


_pair_editor("Force pairs (pin a student→mentor)", "force_pairs", "force")
_pair_editor("Block pairs (forbid a student→mentor)", "block_pairs", "block")
sb.multiselect("Skip students", options=list(_student_label),
               format_func=lambda i: _student_label[i], key="skip_s")
sb.multiselect("Skip mentors", options=list(_mentor_label),
               format_func=lambda i: _mentor_label[i], key="skip_m")


def current_overrides() -> Overrides:
    return Overrides(
        force=[Pair(student_id=a, mentor_id=b) for a, b in st.session_state.force_pairs],
        block=[Pair(student_id=a, mentor_id=b) for a, b in st.session_state.block_pairs],
        skip_students=list(st.session_state.get("skip_s", [])),
        skip_mentors=list(st.session_state.get("skip_m", [])),
    )


def build_config(focus=0.0, trait=0.0, symptom=0.0, mentor_pref=0.0) -> Config:
    """Config from the shared Q1 hard-constraints + the given (per-question) weights."""
    s = st.session_state
    return Config(
        session_length_minutes=s.get("q1_session_len", file_cfg.session_length_minutes),
        max_students_per_mentor=int(s.get("q1_max_cap", file_cfg.max_students_per_mentor or 12)),
        enforce_gender=s.get("q1_enforce_gender", file_cfg.enforce_gender),
        weights=Weights(focus_overlap=focus, trait_match=trait,
                        symptom_fit=symptom, mentor_pref=mentor_pref),
        thresholds=Thresholds(min_acceptable_score=s.get("q23_min_acc",
                                                         file_cfg.thresholds.min_acceptable_score),
                              poor_fit_threshold=s.get("q3_poor_fit",
                                                       file_cfg.thresholds.poor_fit_threshold)),
        rejection_probability=s.get("q4_reject", file_cfg.rejection_probability),
        random_seed=int(s.get("q4_seed", file_cfg.random_seed)),
        engine=s.get("q1_engine", file_cfg.engine),
        enrichment=file_cfg.enrichment,
    )


# ----------------------------- display helpers ----------------------------
def show_assignments(res, key):
    df = pd.DataFrame(res.assignments)
    st.dataframe(df, use_container_width=True, height=380)
    st.download_button("⬇ assignments.csv", df.to_csv(index=False),
                       f"{key}_assignments.csv", "text/csv", key=f"dl_{key}")


def show_unassigned(res):
    u = pd.DataFrame(res.unassigned)
    if u.empty:
        st.success("Everyone matched.")
        return
    st.dataframe(u["reason"].value_counts().rename_axis("reason").reset_index(name="count"),
                 use_container_width=True)
    st.dataframe(u, use_container_width=True, height=240)


def show_metrics(res, cfg, baseline=None):
    s = summarize(res, len(st.session_state.students), cfg)
    cols = st.columns(5)
    cols[0].metric("Matched", f"{s['matched']}/{s['total_students']}",
                   f"{s['coverage']*100:.1f}% coverage")
    delta = None
    if baseline is not None:
        delta = baseline_delta(res, baseline, len(st.session_state.students), cfg)
    cols[1].metric("Mean score", f"{s['mean_score']:.3f}",
                   f"{delta['mean_score_delta']:+.3f} vs random" if delta else None)
    cols[2].metric("Median score", f"{s['median_score']:.3f}")
    cols[3].metric("% above acceptable", f"{s['pct_above_min_acceptable']*100:.1f}%")
    cols[4].metric("Review queue", s["review_queue_size"])


tabs = st.tabs(["📁 Data", "🤖 Enrichment",
                "1️⃣ Q1 · Feasible", "2️⃣ Q2 · Parent expectations",
                "3️⃣ Q3 · Two-way fit", "4️⃣ Q4 · Rejection & re-match"])

# ============================== DATA TAB ==================================
with tabs[0]:
    src = st.session_state.data_source
    c1, c2, c3 = st.columns(3)
    c1.metric("Students", len(st.session_state.students))
    c2.metric("Mentors", len(st.session_state.mentors))
    c3.metric("Active dataset", src)

    st.subheader("⬆️ Upload / reset dataset")
    st.caption("Upload replacement CSVs (same columns). Leave one empty to keep the current one.")
    uc1, uc2 = st.columns(2)
    up_s = uc1.file_uploader("Students CSV", type="csv", key="up_s")
    up_m = uc2.file_uploader("Mentors CSV", type="csv", key="up_m")
    uc1.caption("Required: " + ", ".join(STUDENT_COLUMNS))
    uc2.caption("Required: " + ", ".join(MENTOR_COLUMNS))
    b1, b2 = st.columns(2)
    if b1.button("📥 Load uploaded data", type="primary", disabled=not (up_s or up_m)):
        try:
            sdf = pd.read_csv(up_s) if up_s else st.session_state.students_df
            mdf = pd.read_csv(up_m) if up_m else st.session_state.mentors_df
            miss = ([f"students: {c}" for c in validate_columns(sdf, STUDENT_COLUMNS)] if up_s else []) \
                + ([f"mentors: {c}" for c in validate_columns(mdf, MENTOR_COLUMNS)] if up_m else [])
            if miss:
                st.error("Missing columns → " + "; ".join(miss))
            else:
                # Replace the dataset in Supabase (the new data replaces the old).
                saved = False
                if up_s:
                    saved = store_mod.dataset_replace("student", _records(sdf)) or saved
                if up_m:
                    saved = store_mod.dataset_replace("mentor", _records(mdf)) or saved
                set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf,
                            "supabase" if saved else "uploaded")
                where = "replaced in Supabase" if saved else "loaded (session only — no Supabase)"
                st.success(f"{len(sdf)} students × {len(mdf)} mentors {where}. Re-run the questions.")
                st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not parse: {e}")
    if b2.button("♻️ Reset to default data", disabled=src == "default"):
        load_default_dataset(persist=True)
        st.rerun()

    st.subheader("🧠 Enrichment cache")
    sc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.srecs.values()))
    mc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.mrecs.values()))
    st.caption(f"Backend: **{store_mod.backend_name()}** · students: {sc} · mentors: {mc}")
    e1, e2, e3 = st.columns(3)
    if e1.button("💾 Save tags to cache"):
        enrich_mod.save_cache(file_cfg, "student", st.session_state.srecs)
        enrich_mod.save_cache(file_cfg, "mentor", st.session_state.mrecs)
        st.success("Saved.")
    e2.download_button("⬇ students_enriched.json",
                       json.dumps(st.session_state.srecs, ensure_ascii=False, indent=2),
                       "students_enriched.json", "application/json")
    e3.download_button("⬇ mentors_enriched.json",
                       json.dumps(st.session_state.mrecs, ensure_ascii=False, indent=2),
                       "mentors_enriched.json", "application/json")

    st.subheader("👀 Current data")
    dt1, dt2 = st.tabs([f"Students ({len(st.session_state.students)})",
                        f"Mentors ({len(st.session_state.mentors)})"])
    dt1.dataframe(st.session_state.students_df, use_container_width=True, height=360)
    dt2.dataframe(st.session_state.mentors_df, use_container_width=True, height=360)

# ============================== ENRICHMENT TAB ===========================
with tabs[1]:
    st.subheader("🤖 LLM enrichment (OpenAI)")
    st.caption("Turns the messy VI/EN text into structured tags used by Q2 and Q3. "
               "Q1 does not need it. Tags persist to the active backend.")
    key = integrated_key()
    if key:
        st.success("🔑 OpenAI key loaded from environment.")
    else:
        st.warning("No OPENAI_API_KEY found. Q1 still runs; Q2/Q3 need enrichment.")
    st.caption(f"Persistence backend: **{store_mod.backend_name()}**")
    c1, c2, c3 = st.columns([2, 1, 1])
    model = c1.text_input("Model", value=file_cfg.enrichment.resolve_model())
    kind = c2.selectbox("Target", ["student", "mentor"])
    pool = st.session_state.students if kind == "student" else st.session_state.mentors
    sample = c3.number_input("Sample rows", 1, len(pool), min(25, len(pool)), 25)
    all_rows = st.checkbox(f"Enrich ALL {len(pool)} {kind}s (slower / costlier)")
    if st.button("▶ Run enrichment", type="primary", disabled=not key):
        items = pool if all_rows else pool[: int(sample)]
        bar = st.progress(0.0, text="Calling OpenAI…")
        recs = enrich_mod.enrich_sync(
            items, kind, model, key, file_cfg.enrichment.max_workers,
            file_cfg.enrichment.max_retries,
            progress_cb=lambda d, t: bar.progress(d / t, text=f"Enriched {d}/{t}"))
        full = st.session_state.srecs if kind == "student" else st.session_state.mrecs
        full.update(recs)
        enrich_mod.save_cache(file_cfg, kind, full)
        bar.empty()
        n_failed = sum(1 for r in recs.values() if r.get("llm_failed"))
        msg = f"Enriched {len(recs)} {kind} rows — saved to {store_mod.backend_name()}."
        if n_failed:
            msg += f" ({n_failed} stayed unenriched after retries.)"
        st.success(msg + " Re-run Q2/Q3 to use the new tags.")
    sc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.srecs.values()))
    mc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.mrecs.values()))
    st.caption(f"Tags by source — students: {sc} · mentors: {mc}")

# ============================== Q1 TAB ===================================
with tabs[2]:
    st.subheader("Q1 · Feasible matching (hard constraints only)")
    st.caption("Assign each student to one mentor satisfying **gender + time + capacity**. "
               "No preference scoring here.")
    c1, c2 = st.columns(2)
    c1.slider("Session length (min)", 15, 120, file_cfg.session_length_minutes, 15, key="q1_session_len")
    c2.slider("Max students per mentor", 1, 30, file_cfg.max_students_per_mentor or 12, key="q1_max_cap")
    c1.checkbox("Enforce requested gender (hard)", file_cfg.enforce_gender, key="q1_enforce_gender")
    c2.selectbox("Engine", ["optimal", "greedy"],
                 index=0 if file_cfg.engine == "optimal" else 1, key="q1_engine")
    if st.button("▶ Run Q1", type="primary", key="run_q1"):
        cfg = build_config()  # all weights 0 -> pure feasibility
        st.session_state.q1 = (run_matching(st.session_state.students, st.session_state.mentors,
                                            st.session_state.srecs, st.session_state.mrecs,
                                            cfg, current_overrides(), engine=cfg.engine), cfg)
    if "q1" in st.session_state:
        res, cfg = st.session_state.q1
        show_metrics(res, cfg)
        t1, t2 = st.tabs(["✅ Assignments", "🚫 Unassigned (why)"])
        with t1:
            show_assignments(res, "q1")
        with t2:
            show_unassigned(res)
    else:
        st.info("Click **Run Q1** to compute the feasible matching.")

# ============================== Q2 TAB ===================================
with tabs[3]:
    st.subheader("Q2 · Parent / student expectations")
    st.caption("Among feasible pairs, prefer mentors whose focus areas and traits match what the "
               "parent/student asked for. Weights below serve **Q2**.")
    c1, c2 = st.columns(2)
    f = c1.slider("Q2 · focus-overlap weight", 0.0, 2.0, file_cfg.weights.focus_overlap, 0.1, key="q2_focus")
    t = c2.slider("Q2 · trait-match weight", 0.0, 2.0, file_cfg.weights.trait_match, 0.1, key="q2_trait")
    st.slider("Min acceptable score (metric)", 0.0, 1.0,
              file_cfg.thresholds.min_acceptable_score, 0.05, key="q23_min_acc")
    if st.button("▶ Run Q2", type="primary", key="run_q2"):
        cfg = build_config(focus=f, trait=t)
        res = run_matching(st.session_state.students, st.session_state.mentors,
                           st.session_state.srecs, st.session_state.mrecs,
                           cfg, current_overrides(), engine=cfg.engine)
        base = run_matching(st.session_state.students, st.session_state.mentors,
                            st.session_state.srecs, st.session_state.mrecs,
                            cfg, current_overrides(), engine="random")
        st.session_state.q2 = (res, cfg, base)
    if "q2" in st.session_state:
        res, cfg, base = st.session_state.q2
        show_metrics(res, cfg, baseline=base)
        show_assignments(res, "q2")
    else:
        st.info("Click **Run Q2**. (Run enrichment first for non-zero scores.)")

# ============================== Q3 TAB ===================================
with tabs[4]:
    st.subheader("Q3 · Two-way fit (mentor preferences + student symptoms)")
    st.caption("Extends Q2: also weighs the student's symptom needs and the mentor's own "
               "preferred-student profile. Weights below serve **Q3** and build on Q2's weights.")
    c1, c2 = st.columns(2)
    sym = c1.slider("Q3 · symptom-fit weight", 0.0, 2.0, file_cfg.weights.symptom_fit, 0.1, key="q3_symptom")
    mp = c2.slider("Q3 · mentor-preference weight", 0.0, 2.0, file_cfg.weights.mentor_pref, 0.1, key="q3_pref")
    st.slider("Poor-fit threshold (review queue)", 0.0, 1.0,
              file_cfg.thresholds.poor_fit_threshold, 0.05, key="q3_poor_fit")
    st.caption(f"Inherits Q2 weights — focus: {st.session_state.get('q2_focus', file_cfg.weights.focus_overlap)}, "
               f"trait: {st.session_state.get('q2_trait', file_cfg.weights.trait_match)} (set in the Q2 tab).")
    if st.button("▶ Run Q3", type="primary", key="run_q3"):
        cfg = build_config(focus=st.session_state.get("q2_focus", file_cfg.weights.focus_overlap),
                           trait=st.session_state.get("q2_trait", file_cfg.weights.trait_match),
                           symptom=sym, mentor_pref=mp)
        res = run_matching(st.session_state.students, st.session_state.mentors,
                           st.session_state.srecs, st.session_state.mrecs,
                           cfg, current_overrides(), engine=cfg.engine)
        base = run_matching(st.session_state.students, st.session_state.mentors,
                            st.session_state.srecs, st.session_state.mrecs,
                            cfg, current_overrides(), engine="random")
        st.session_state.q3 = (res, cfg, base)
    if "q3" in st.session_state:
        res, cfg, base = st.session_state.q3
        show_metrics(res, cfg, baseline=base)
        t1, t2 = st.tabs(["✅ Assignments", "⚠️ Review queue (poor fits)"])
        with t1:
            show_assignments(res, "q3")
        with t2:
            st.dataframe(pd.DataFrame(res.review_queue), use_container_width=True, height=360)
    else:
        st.info("Click **Run Q3**. (Run enrichment first for non-zero scores.)")

# ============================== Q4 TAB ===================================
with tabs[5]:
    st.subheader("Q4 · Rejection & re-matching")
    st.caption("Take the Q3 match, simulate students rejecting their mentor, then re-match the "
               "rejected ones (barred from their old mentor). Parameters below serve **Q4**.")
    c1, c2 = st.columns(2)
    c1.slider("Rejection probability", 0.0, 0.5, file_cfg.rejection_probability, 0.05, key="q4_reject")
    c2.number_input("Random seed", value=file_cfg.random_seed, step=1, key="q4_seed")
    if st.button("▶ Run Q4", type="primary", key="run_q4"):
        cfg = build_config(focus=st.session_state.get("q2_focus", file_cfg.weights.focus_overlap),
                           trait=st.session_state.get("q2_trait", file_cfg.weights.trait_match),
                           symptom=st.session_state.get("q3_symptom", file_cfg.weights.symptom_fit),
                           mentor_pref=st.session_state.get("q3_pref", file_cfg.weights.mentor_pref))
        st.session_state.q4 = (simulate_and_rematch(
            st.session_state.students, st.session_state.mentors,
            st.session_state.srecs, st.session_state.mrecs, cfg, current_overrides()), cfg)
    if "q4" in st.session_state:
        rr, cfg = st.session_state.q4
        before = summarize(rr.initial, len(st.session_state.students), cfg)
        after = summarize(rr.final, len(st.session_state.students), cfg)
        m = st.columns(4)
        m[0].metric("Rejected", len(rr.rejected_ids))
        m[1].metric("Mean score before", f"{before['mean_score']:.3f}")
        m[2].metric("Mean score after", f"{after['mean_score']:.3f}",
                    f"{after['mean_score']-before['mean_score']:+.3f}")
        m[3].metric("Coverage after", f"{after['coverage']*100:.1f}%")
        show_assignments(rr.final, "q4")
    else:
        st.info("Click **Run Q4**. (It uses the Q3 weights; run Q3/enrichment first.)")
