"""Streamlit UI for the mentor-student matcher.

Lets the interviewer tune rules/weights, apply manual overrides, run the LLM
enrichment live, and see assignments + quality metrics — all recomputed on change.
Runs offline from the committed cache; live enrichment is optional.
"""
from __future__ import annotations

import collections
import os
import sys
from pathlib import Path

# Make `matcher` importable whether or not the package is installed.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import streamlit as st

from matcher import enrich as enrich_mod
from matcher.config import Config, Enrichment, Overrides, Pair, Thresholds, Weights, load_config
from matcher.data_io import load_mentors, load_students
from matcher.matcher import run_matching
from matcher.metrics import baseline_delta, summarize
from matcher.rematch import simulate_and_rematch

st.set_page_config(page_title="TeenCare Mentor Matcher", layout="wide")


@st.cache_data(show_spinner=False)
def _load():
    return load_students(), load_mentors()


def _api_key(ui_key: str) -> str | None:
    if ui_key:
        return ui_key
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")


students, mentors = _load()
file_cfg = load_config()

# Enrichment records live in session state so live runs persist across reruns.
if "srecs" not in st.session_state:
    s0, m0 = enrich_mod.get_enrichment(students, mentors, file_cfg)
    st.session_state.srecs, st.session_state.mrecs = s0, m0

st.title("🎯 TeenCare Mentor–Student Matcher")
st.caption("Rule-driven, tunable matching · 2,000 students × 200 mentors · "
           "constraints → scoring → assignment → metrics")

# ----------------------------- sidebar: config ----------------------------
sb = st.sidebar
sb.header("⚙️ Rules & weights")
session_len = sb.slider("Session length (min)", 15, 120, file_cfg.session_length_minutes, 15)
max_cap = sb.slider("Max students per mentor", 1, 30, file_cfg.max_students_per_mentor or 12)
enforce_gender = sb.checkbox("Enforce requested gender (hard)", file_cfg.enforce_gender)
engine = sb.selectbox("Engine", ["optimal", "greedy"],
                      index=0 if file_cfg.engine == "optimal" else 1)

sb.subheader("Scoring weights")
w = file_cfg.weights
w_focus = sb.slider("focus overlap", 0.0, 2.0, w.focus_overlap, 0.1)
w_trait = sb.slider("trait match", 0.0, 2.0, w.trait_match, 0.1)
w_symptom = sb.slider("symptom fit", 0.0, 2.0, w.symptom_fit, 0.1)
w_pref = sb.slider("mentor preference", 0.0, 2.0, w.mentor_pref, 0.1)

sb.subheader("Thresholds")
min_acc = sb.slider("min acceptable score", 0.0, 1.0, file_cfg.thresholds.min_acceptable_score, 0.05)
poor_fit = sb.slider("poor-fit (review queue)", 0.0, 1.0, file_cfg.thresholds.poor_fit_threshold, 0.05)
reject_p = sb.slider("Q4 rejection probability", 0.0, 0.5, file_cfg.rejection_probability, 0.05)
seed = sb.number_input("random seed", value=file_cfg.random_seed, step=1)


def current_config() -> Config:
    return Config(
        session_length_minutes=session_len,
        max_students_per_mentor=int(max_cap),
        enforce_gender=enforce_gender,
        weights=Weights(focus_overlap=w_focus, trait_match=w_trait,
                        symptom_fit=w_symptom, mentor_pref=w_pref),
        thresholds=Thresholds(min_acceptable_score=min_acc, poor_fit_threshold=poor_fit),
        rejection_probability=reject_p,
        random_seed=int(seed),
        engine=engine,
        enrichment=file_cfg.enrichment,
    )


# ----------------------------- overrides ----------------------------------
sb.header("✍️ Manual overrides")
sb.caption("One per line. Pairs as `student_id,mentor_id`.")
force_txt = sb.text_area("Force pairs", height=70, key="force")
block_txt = sb.text_area("Block pairs", height=70, key="block")
skip_s_txt = sb.text_area("Skip students (ids)", height=60, key="skips")
skip_m_txt = sb.text_area("Skip mentors (ids)", height=60, key="skipm")


def parse_pairs(txt):
    out = []
    for line in txt.splitlines():
        line = line.strip()
        if "," in line:
            a, b = line.split(",", 1)
            out.append(Pair(student_id=a.strip(), mentor_id=b.strip()))
    return out


def current_overrides() -> Overrides:
    return Overrides(
        force=parse_pairs(force_txt), block=parse_pairs(block_txt),
        skip_students=[x.strip() for x in skip_s_txt.splitlines() if x.strip()],
        skip_mentors=[x.strip() for x in skip_m_txt.splitlines() if x.strip()],
    )


# ----------------------------- LLM enrichment -----------------------------
st.subheader("🤖 LLM enrichment (live)")
with st.expander("Run OpenAI enrichment on the messy VI/EN text → structured tags", expanded=False):
    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    ui_key = c1.text_input("OpenAI API key", type="password",
                           help="Falls back to st.secrets / OPENAI_API_KEY env.")
    model = c2.text_input("Model", value=file_cfg.enrichment.resolve_model())
    kind = c3.selectbox("Target", ["student", "mentor"])
    sample = c4.number_input("Sample rows", min_value=1,
                             max_value=2000, value=25, step=25,
                             help="Enrich the first N rows live (keeps cost low).")
    if st.button("▶ Run enrichment", type="primary"):
        key = _api_key(ui_key)
        if not key:
            st.error("No API key provided (and none in secrets/env).")
        else:
            items = (students if kind == "student" else mentors)[: int(sample)]
            bar = st.progress(0.0, text="Calling OpenAI…")
            recs = enrich_mod.enrich_sync(
                items, kind, model, key, file_cfg.enrichment.max_workers,
                progress_cb=lambda d, t: bar.progress(d / t, text=f"Enriched {d}/{t}"))
            target = st.session_state.srecs if kind == "student" else st.session_state.mrecs
            target.update(recs)
            bar.empty()
            st.success(f"Live-enriched {len(recs)} {kind} rows with {model}.")

# Source provenance (llm vs keyword) across the whole dataset.
def _src_counts(recs):
    return collections.Counter(r.get("source", "keyword") for r in recs.values())

sc, mc = _src_counts(st.session_state.srecs), _src_counts(st.session_state.mrecs)
st.caption(f"Enrichment source — students: {dict(sc)} · mentors: {dict(mc)}")

# ----------------------------- run matching -------------------------------
cfg = current_config()
ov = current_overrides()
srecs, mrecs = st.session_state.srecs, st.session_state.mrecs

result = run_matching(students, mentors, srecs, mrecs, cfg, ov, engine=cfg.engine)
baseline = run_matching(students, mentors, srecs, mrecs, cfg, ov, engine="random")
summary = summarize(result, len(students), cfg)
delta = baseline_delta(result, baseline, len(students), cfg)

st.subheader("📊 Match quality")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Matched", f"{summary['matched']}/{summary['total_students']}",
          f"{summary['coverage']*100:.1f}% coverage")
m2.metric("Mean score", f"{summary['mean_score']:.3f}",
          f"{delta['mean_score_delta']:+.3f} vs random")
m3.metric("Median score", f"{summary['median_score']:.3f}")
m4.metric("% above acceptable", f"{summary['pct_above_min_acceptable']*100:.1f}%")
m5.metric("Review queue", summary["review_queue_size"])

tabs = st.tabs(["✅ Assignments", "🚫 Unassigned", "⚠️ Review queue", "🔁 Q4 re-match"])

with tabs[0]:
    df = pd.DataFrame(result.assignments)
    st.dataframe(df, use_container_width=True, height=420)
    st.download_button("Download assignments.csv", df.to_csv(index=False),
                       "assignments.csv", "text/csv")

with tabs[1]:
    u = pd.DataFrame(result.unassigned)
    if not u.empty:
        st.dataframe(u["reason"].value_counts().rename_axis("reason").reset_index(name="count"),
                     use_container_width=True)
        st.dataframe(u, use_container_width=True, height=300)
    else:
        st.success("Everyone matched.")

with tabs[2]:
    rq = pd.DataFrame(result.review_queue)
    st.caption(f"Feasible pairs scoring below the poor-fit threshold ({poor_fit:.2f}).")
    st.dataframe(rq, use_container_width=True, height=420)

with tabs[3]:
    st.caption(f"Simulate ~{reject_p*100:.0f}% of students rejecting their mentor, then re-match.")
    if st.button("Run Q4 simulation"):
        rr = simulate_and_rematch(students, mentors, srecs, mrecs, cfg, ov)
        before = summarize(rr.initial, len(students), cfg)
        after = summarize(rr.final, len(students), cfg)
        a, b, c = st.columns(3)
        a.metric("Rejected", len(rr.rejected_ids))
        b.metric("Mean score before", f"{before['mean_score']:.3f}")
        c.metric("Mean score after", f"{after['mean_score']:.3f}",
                 f"{after['mean_score']-before['mean_score']:+.3f}")
        st.dataframe(pd.DataFrame(rr.final.assignments), use_container_width=True, height=360)
