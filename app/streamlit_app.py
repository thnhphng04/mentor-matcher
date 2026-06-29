"""Streamlit UI for the mentor-student matcher.

Tune rules/weights, manage the dataset (view / upload / reset), run the OpenAI
enrichment live, and see assignments + quality metrics — recomputed on change.
The OpenAI key is auto-loaded from the environment / Streamlit secrets, so there
is nothing to paste on open. Runs offline from the committed cache without a key.
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
from matcher.config import (Config, Overrides, Pair, Thresholds, Weights, load_config)
from matcher.data_io import (MENTOR_COLUMNS, STUDENT_COLUMNS, load_mentors, load_students,
                             mentors_from_df, students_from_df, validate_columns, ROOT)
from matcher.matcher import run_matching
from matcher.metrics import baseline_delta, summarize
from matcher.rematch import simulate_and_rematch

st.set_page_config(page_title="TeenCare Mentor Matcher", layout="wide")
file_cfg = load_config()

DEFAULT_STUDENTS = ROOT / "data" / "students_prod_2000_enriched.csv"
DEFAULT_MENTORS = ROOT / "data" / "mentors_prod_200_enriched.csv"


# --------------------------------------------------------------------------
# Dataset state — held in session so uploads/resets swap the active data.
# --------------------------------------------------------------------------
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


def load_default_dataset():
    sdf, mdf = pd.read_csv(DEFAULT_STUDENTS), pd.read_csv(DEFAULT_MENTORS)
    set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf, "default")


if "students" not in st.session_state:
    load_default_dataset()


def integrated_key() -> str | None:
    """Resolve the OpenAI key from Streamlit secrets or environment — no UI."""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")


st.title("🎯 TeenCare Mentor–Student Matcher")
st.caption("Rule-driven, tunable matching · constraints → scoring → assignment → metrics")

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

sb.header("✍️ Manual overrides")
sb.caption("One per line. Pairs as `student_id,mentor_id`.")
force_txt = sb.text_area("Force pairs", height=70, key="force")
block_txt = sb.text_area("Block pairs", height=70, key="block")
skip_s_txt = sb.text_area("Skip students (ids)", height=60, key="skips")
skip_m_txt = sb.text_area("Skip mentors (ids)", height=60, key="skipm")


def current_config() -> Config:
    return Config(
        session_length_minutes=session_len,
        max_students_per_mentor=int(max_cap),
        enforce_gender=enforce_gender,
        weights=Weights(focus_overlap=w_focus, trait_match=w_trait,
                        symptom_fit=w_symptom, mentor_pref=w_pref),
        thresholds=Thresholds(min_acceptable_score=min_acc, poor_fit_threshold=poor_fit),
        rejection_probability=reject_p, random_seed=int(seed),
        engine=engine, enrichment=file_cfg.enrichment,
    )


def _parse_pairs(txt):
    out = []
    for line in txt.splitlines():
        if "," in line:
            a, b = line.split(",", 1)
            out.append(Pair(student_id=a.strip(), mentor_id=b.strip()))
    return out


def current_overrides() -> Overrides:
    return Overrides(
        force=_parse_pairs(force_txt), block=_parse_pairs(block_txt),
        skip_students=[x.strip() for x in skip_s_txt.splitlines() if x.strip()],
        skip_mentors=[x.strip() for x in skip_m_txt.splitlines() if x.strip()],
    )


tab_data, tab_match = st.tabs(["📁 Data", "🎯 Matching"])

# ============================== DATA TAB ==================================
with tab_data:
    src = st.session_state.data_source
    c1, c2, c3 = st.columns(3)
    c1.metric("Students", len(st.session_state.students))
    c2.metric("Mentors", len(st.session_state.mentors))
    c3.metric("Active dataset", src)

    st.subheader("⬆️ Upload / reset dataset")
    st.caption("Upload replacement CSVs (must keep the same columns). Leave one empty to "
               "keep the current one. Uploads live for this session only.")
    uc1, uc2 = st.columns(2)
    up_s = uc1.file_uploader("Students CSV", type="csv", key="up_s")
    up_m = uc2.file_uploader("Mentors CSV", type="csv", key="up_m")
    uc1.caption("Required columns: " + ", ".join(STUDENT_COLUMNS))
    uc2.caption("Required columns: " + ", ".join(MENTOR_COLUMNS))

    b1, b2 = st.columns([1, 1])
    if b1.button("📥 Load uploaded data", type="primary", disabled=not (up_s or up_m)):
        try:
            sdf = pd.read_csv(up_s) if up_s else st.session_state.students_df
            mdf = pd.read_csv(up_m) if up_m else st.session_state.mentors_df
            miss = []
            if up_s:
                miss += [f"students: {c}" for c in validate_columns(sdf, STUDENT_COLUMNS)]
            if up_m:
                miss += [f"mentors: {c}" for c in validate_columns(mdf, MENTOR_COLUMNS)]
            if miss:
                st.error("Missing required columns → " + "; ".join(miss))
            else:
                set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf, "uploaded")
                st.success(f"Loaded {len(sdf)} students × {len(mdf)} mentors.")
                st.rerun()
        except Exception as e:  # noqa: BLE001 — surface parse errors to the user
            st.error(f"Could not parse uploaded data: {e}")

    if b2.button("♻️ Reset to default data", disabled=src == "default"):
        load_default_dataset()
        st.success("Reverted to the bundled dataset.")
        st.rerun()

    st.subheader("👀 Current data")
    dt1, dt2 = st.tabs([f"Students ({len(st.session_state.students)})",
                        f"Mentors ({len(st.session_state.mentors)})"])
    with dt1:
        st.dataframe(st.session_state.students_df, use_container_width=True, height=380)
        st.download_button("Download students.csv",
                           st.session_state.students_df.to_csv(index=False),
                           "students.csv", "text/csv")
    with dt2:
        st.dataframe(st.session_state.mentors_df, use_container_width=True, height=380)
        st.download_button("Download mentors.csv",
                           st.session_state.mentors_df.to_csv(index=False),
                           "mentors.csv", "text/csv")

# ============================== MATCHING TAB ==============================
with tab_match:
    students = st.session_state.students
    mentors = st.session_state.mentors
    srecs, mrecs = st.session_state.srecs, st.session_state.mrecs

    # ---- LLM enrichment (key auto-loaded) ----
    st.subheader("🤖 LLM enrichment (live)")
    key = integrated_key()
    with st.expander("Run OpenAI enrichment on the messy VI/EN text → structured tags",
                     expanded=False):
        if key:
            st.success("🔑 OpenAI key loaded from environment — no input needed.")
        else:
            st.warning("No OPENAI_API_KEY in secrets/env. Set it on Render (or "
                       ".streamlit/secrets.toml) to enable live enrichment. "
                       "Matching still works on the offline cache.")
        c1, c2, c3 = st.columns([2, 1, 1])
        model = c1.text_input("Model", value=file_cfg.enrichment.resolve_model())
        kind = c2.selectbox("Target", ["student", "mentor"])
        sample = c3.number_input("Sample rows", 1, 2000, 25, 25,
                                 help="Enrich the first N rows live (keeps cost low).")
        if st.button("▶ Run enrichment", type="primary", disabled=not key):
            items = (students if kind == "student" else mentors)[: int(sample)]
            bar = st.progress(0.0, text="Calling OpenAI…")
            recs = enrich_mod.enrich_sync(
                items, kind, model, key, file_cfg.enrichment.max_workers,
                progress_cb=lambda d, t: bar.progress(d / t, text=f"Enriched {d}/{t}"))
            (st.session_state.srecs if kind == "student" else st.session_state.mrecs).update(recs)
            bar.empty()
            st.success(f"Live-enriched {len(recs)} {kind} rows with {model}.")
            srecs, mrecs = st.session_state.srecs, st.session_state.mrecs

    def _src_counts(recs):
        return dict(collections.Counter(r.get("source", "keyword") for r in recs.values()))
    st.caption(f"Enrichment source — students: {_src_counts(srecs)} · mentors: {_src_counts(mrecs)}")

    # ---- run matching ----
    cfg = current_config()
    ov = current_overrides()
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
        st.caption(f"Feasible pairs scoring below the poor-fit threshold ({poor_fit:.2f}).")
        st.dataframe(pd.DataFrame(result.review_queue), use_container_width=True, height=420)
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
