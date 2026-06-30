"""Streamlit UI for the mentor-student matcher (bilingual EN/VI).

Sidebar: language toggle + page selector (Matcher · Instruction · Description).
Matcher page = Data · Enrichment · Q1 · Q2 · Q3 · Q4 tabs. Each question is
self-contained — its own controls and a Run button (no live auto-recompute).
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for i18n

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import pandas as pd
import streamlit as st

from i18n import LANGS, page_md, t
from matcher import enrich as enrich_mod
from matcher import store as store_mod
from matcher.config import Config, Overrides, Pair, Thresholds, Weights, load_config
from matcher.data_io import (MENTOR_COLUMNS, STUDENT_COLUMNS, mentors_from_df,
                             students_from_df, validate_columns, ROOT)
from matcher.matcher import run_matching
from matcher.metrics import baseline_delta, summarize
from matcher.rematch import simulate_and_rematch

st.set_page_config(page_title="TeenCare Mentor Matcher", layout="wide")

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
    return df.where(pd.notna(df), None).to_dict("records")


def load_default_dataset(persist: bool = False):
    sdf, mdf = pd.read_csv(DEFAULT_STUDENTS), pd.read_csv(DEFAULT_MENTORS)
    if persist:
        store_mod.dataset_replace("student", [])
        store_mod.dataset_replace("mentor", [])
    set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf, "default")


def load_initial_dataset():
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


# --------------------------- shared config / overrides --------------------
def build_config(focus=0.0, trait=0.0, symptom=0.0, mentor_pref=0.0) -> Config:
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


def current_overrides() -> Overrides:
    s = st.session_state
    return Overrides(
        force=[Pair(student_id=a, mentor_id=b) for a, b in s.get("force_pairs", [])],
        block=[Pair(student_id=a, mentor_id=b) for a, b in s.get("block_pairs", [])],
        skip_students=list(s.get("skip_s", [])),
        skip_mentors=list(s.get("skip_m", [])),
    )


def _match(cfg, engine):
    return run_matching(st.session_state.students, st.session_state.mentors,
                        st.session_state.srecs, st.session_state.mrecs,
                        cfg, current_overrides(), engine=engine)


# ----------------------------- display helpers ----------------------------
def show_assignments(res, key):
    df = pd.DataFrame(res.assignments)
    st.dataframe(df, use_container_width=True, height=380)
    st.download_button(t("dl_assignments"), df.to_csv(index=False),
                       f"{key}_assignments.csv", "text/csv", key=f"dl_{key}")


def show_unassigned(res):
    u = pd.DataFrame(res.unassigned)
    if u.empty:
        st.success(t("everyone_matched"))
        return
    st.dataframe(u["reason"].value_counts().rename_axis(t("reason")).reset_index(name=t("count")),
                 use_container_width=True)
    st.dataframe(u, use_container_width=True, height=240)


def show_metrics(res, cfg, baseline=None):
    s = summarize(res, len(st.session_state.students), cfg)
    c = st.columns(5)
    c[0].metric(t("matched"), f"{s['matched']}/{s['total_students']}",
                t("coverage_delta", pct=f"{s['coverage']*100:.1f}"))
    delta = baseline_delta(res, baseline, len(st.session_state.students), cfg) if baseline is not None else None
    c[1].metric(t("mean_score"), f"{s['mean_score']:.3f}",
                t("vs_random", d=f"{delta['mean_score_delta']:+.3f}") if delta else None)
    c[2].metric(t("median_score"), f"{s['median_score']:.3f}")
    c[3].metric(t("pct_above"), f"{s['pct_above_min_acceptable']*100:.1f}%")
    c[4].metric(t("review_size"), s["review_queue_size"])


def enriched_df(kind):
    """Flatten the enrichment tag records into a readable DataFrame."""
    if kind == "student":
        names = {s.id: s.name for s in st.session_state.students}
        return pd.DataFrame([{
            "id": sid, "name": names.get(sid, ""),
            "requested_mentor_gender": r.get("requested_mentor_gender"),
            "desired_focus": ", ".join(r.get("desired_focus", [])),
            "desired_traits": ", ".join(r.get("desired_traits", [])),
            "symptom_category": r.get("symptom_category"),
            "source": r.get("source"),
        } for sid, r in st.session_state.srecs.items()])
    names = {m.id: m.name for m in st.session_state.mentors}
    rows = []
    for mid, r in st.session_state.mrecs.items():
        ps = r.get("preferred_student") or {}
        rows.append({
            "id": mid, "name": names.get(mid, ""),
            "personality_tags": ", ".join(r.get("personality_tags", [])),
            "offered_focus": ", ".join(r.get("offered_focus", [])),
            "pref_grade_band": ps.get("grade_band"),
            "pref_needs": ", ".join(ps.get("needs", [])),
            "source": r.get("source"),
        })
    return pd.DataFrame(rows)


def upload_and_enrich(sdf, mdf, up_s, up_m):
    """Replace the dataset (Supabase) and auto-enrich ALL rows of the uploaded
    kind(s); if no API key, load the data unenriched and warn."""
    saved = False
    if up_s:
        saved = store_mod.dataset_replace("student", _records(sdf)) or saved
    if up_m:
        saved = store_mod.dataset_replace("mentor", _records(mdf)) or saved
    set_dataset(students_from_df(sdf), mentors_from_df(mdf), sdf, mdf,
                "supabase" if saved else "uploaded")

    key = integrated_key()
    if not key:
        st.warning(t("upload_no_key_warn"))
        st.rerun()
        return
    model = file_cfg.enrichment.resolve_model()
    for kind, flag in (("student", up_s), ("mentor", up_m)):
        if not flag:
            continue
        items = st.session_state.students if kind == "student" else st.session_state.mentors
        kl = t(f"kind_{kind}")
        bar = st.progress(0.0, text=t("auto_enriching", kind=kl, d=0, n=len(items)))
        recs = enrich_mod.enrich_sync(
            items, kind, model, key, file_cfg.enrichment.max_workers,
            file_cfg.enrichment.max_retries,
            progress_cb=lambda d, n, kl=kl: bar.progress(d / n, text=t("auto_enriching", kind=kl, d=d, n=n)))
        full = st.session_state.srecs if kind == "student" else st.session_state.mrecs
        full.update(recs)
        store_mod.remote_clear(kind)            # replace old tags in Supabase
        enrich_mod.save_cache(file_cfg, kind, full)
        bar.empty()
    st.success(t("auto_enriched_done", backend=store_mod.backend_name()))
    st.rerun()


# ============================= SIDEBAR: language + page ===================
sb = st.sidebar
_cur_lang = st.session_state.get("lang", "en")
st.session_state["lang"] = sb.radio(
    t("language"), options=list(LANGS), format_func=lambda c: LANGS[c],
    index=list(LANGS).index(_cur_lang), horizontal=True, key="lang_sel")
page = sb.radio(t("page"), options=["matcher", "instruction", "description"],
                format_func=lambda p: t(f"page_{p}"), key="page_sel")

st.title(t("title"))
st.caption(t("subtitle"))

# ============================= DOC PAGES ==================================
if page == "instruction":
    st.markdown(page_md("instruction"))
    st.stop()
if page == "description":
    st.markdown(page_md("description"))
    st.stop()

# ============================= MATCHER PAGE ===============================
# --- sidebar overrides ---
sb.header(t("overrides"))
sb.caption(t("overrides_help"))
_student_label = {s.id: f"{s.name} · {s.id[:8]}" for s in st.session_state.students}
_mentor_label = {m.id: f"{m.name} · {m.id[:8]}" for m in st.session_state.mentors}
st.session_state.setdefault("force_pairs", [])
st.session_state.setdefault("block_pairs", [])


def _pair_editor(title, state_key, prefix):
    with sb.expander(title, expanded=False):
        s_sel = st.selectbox(t("student"), options=list(_student_label),
                             format_func=lambda i: _student_label[i], key=f"{prefix}_s")
        m_sel = st.selectbox(t("mentor"), options=list(_mentor_label),
                             format_func=lambda i: _mentor_label[i], key=f"{prefix}_m")
        if st.button(t("add_pair"), key=f"{prefix}_add", use_container_width=True):
            if (s_sel, m_sel) not in st.session_state[state_key]:
                st.session_state[state_key].append((s_sel, m_sel))
        for i, (a, b) in enumerate(st.session_state[state_key]):
            cc = st.columns([5, 1])
            cc[0].caption(f"{_student_label.get(a, a)} → {_mentor_label.get(b, b)}")
            if cc[1].button("❌", key=f"{prefix}_rm{i}"):
                st.session_state[state_key].pop(i)
                st.rerun()


_pair_editor(t("force_pairs"), "force_pairs", "force")
_pair_editor(t("block_pairs"), "block_pairs", "block")
sb.multiselect(t("skip_students"), options=list(_student_label),
               format_func=lambda i: _student_label[i], key="skip_s")
sb.multiselect(t("skip_mentors"), options=list(_mentor_label),
               format_func=lambda i: _mentor_label[i], key="skip_m")

tabs = st.tabs([t("tab_data"), t("tab_q1"), t("tab_q2"), t("tab_q3"), t("tab_q4")])

# ------------------- DATA & ENRICHMENT TAB (merged) -----------------------
with tabs[0]:
    src = st.session_state.data_source
    c1, c2, c3 = st.columns(3)
    c1.metric(t("m_students"), len(st.session_state.students))
    c2.metric(t("m_mentors"), len(st.session_state.mentors))
    c3.metric(t("m_active"), src)

    # --- upload (auto-enrich all) / reset ---
    st.subheader(t("upload_reset"))
    st.caption(t("upload_help"))
    _key = integrated_key()
    st.caption(t("auto_enrich_on", backend=store_mod.backend_name()) if _key else t("auto_enrich_off"))
    uc1, uc2 = st.columns(2)
    up_s = uc1.file_uploader(t("students_csv"), type="csv", key="up_s")
    up_m = uc2.file_uploader(t("mentors_csv"), type="csv", key="up_m")
    uc1.caption(t("required", cols=", ".join(STUDENT_COLUMNS)))
    uc2.caption(t("required", cols=", ".join(MENTOR_COLUMNS)))
    if st.button(t("load_uploaded"), type="primary", disabled=not (up_s or up_m)):
        try:
            sdf = pd.read_csv(up_s) if up_s else st.session_state.students_df
            mdf = pd.read_csv(up_m) if up_m else st.session_state.mentors_df
            miss = ([f"students: {c}" for c in validate_columns(sdf, STUDENT_COLUMNS)] if up_s else []) \
                + ([f"mentors: {c}" for c in validate_columns(mdf, MENTOR_COLUMNS)] if up_m else [])
            if miss:
                st.error(t("missing_cols", cols="; ".join(miss)))
            else:
                upload_and_enrich(sdf, mdf, up_s, up_m)
        except Exception as e:  # noqa: BLE001
            st.error(t("parse_error", err=e))

    # --- cache management ---
    st.subheader(t("enrich_cache"))
    sc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.srecs.values()))
    mc = dict(collections.Counter(r.get("source", "unenriched") for r in st.session_state.mrecs.values()))
    st.caption(t("backend_line", backend=store_mod.backend_name(), sc=sc, mc=mc))
    e1, e2 = st.columns(2)
    e1.download_button(t("dl_students_json"),
                       json.dumps(st.session_state.srecs, ensure_ascii=False, indent=2),
                       "students_enriched.json", "application/json")
    e2.download_button(t("dl_mentors_json"),
                       json.dumps(st.session_state.mrecs, ensure_ascii=False, indent=2),
                       "mentors_enriched.json", "application/json")

    # --- data display: Students/Mentors, raw and enriched in separate frames ---
    st.subheader(t("current_data"))
    dstud, dment = st.tabs([t("students_n", n=len(st.session_state.students)),
                            t("mentors_n", n=len(st.session_state.mentors))])

    def _raw_and_enriched(raw_df, kind):
        with st.container(border=True):
            st.markdown(f"**{t('raw_data')}**")
            st.dataframe(raw_df, use_container_width=True, height=300)
        with st.container(border=True):
            st.markdown(f"**{t('enriched_tags')}**")
            st.dataframe(enriched_df(kind), use_container_width=True, height=300)

    with dstud:
        _raw_and_enriched(st.session_state.students_df, "student")
    with dment:
        _raw_and_enriched(st.session_state.mentors_df, "mentor")

# ------------------------------ Q1 ----------------------------------------
with tabs[1]:
    st.subheader(t("q1_title"))
    st.caption(t("q1_caption"))
    c1, c2 = st.columns(2)
    c1.slider(t("session_len"), 15, 120, file_cfg.session_length_minutes, 15, key="q1_session_len")
    c2.slider(t("max_cap"), 1, 30, file_cfg.max_students_per_mentor or 12, key="q1_max_cap")
    c1.checkbox(t("enforce_gender"), file_cfg.enforce_gender, key="q1_enforce_gender")
    c2.selectbox(t("engine"), ["optimal", "greedy"],
                 index=0 if file_cfg.engine == "optimal" else 1, key="q1_engine")
    if st.button(t("run_q1"), type="primary", key="run_q1"):
        cfg = build_config()
        st.session_state.q1 = (_match(cfg, cfg.engine), cfg)
    if "q1" in st.session_state:
        res, cfg = st.session_state.q1
        show_metrics(res, cfg)
        ta, tb = st.tabs([t("assignments"), t("unassigned_why")])
        with ta:
            show_assignments(res, "q1")
        with tb:
            show_unassigned(res)
    else:
        st.info(t("q1_info"))

# ------------------------------ Q2 ----------------------------------------
with tabs[2]:
    st.subheader(t("q2_title"))
    st.caption(t("q2_caption"))
    c1, c2 = st.columns(2)
    f = c1.slider(t("q2_focus_w"), 0.0, 2.0, file_cfg.weights.focus_overlap, 0.1, key="q2_focus")
    tr = c2.slider(t("q2_trait_w"), 0.0, 2.0, file_cfg.weights.trait_match, 0.1, key="q2_trait")
    st.slider(t("min_acc"), 0.0, 1.0, file_cfg.thresholds.min_acceptable_score, 0.05, key="q23_min_acc")
    if st.button(t("run_q2"), type="primary", key="run_q2"):
        cfg = build_config(focus=f, trait=tr)
        st.session_state.q2 = (_match(cfg, cfg.engine), cfg, _match(cfg, "random"))
    if "q2" in st.session_state:
        res, cfg, base = st.session_state.q2
        show_metrics(res, cfg, baseline=base)
        show_assignments(res, "q2")
    else:
        st.info(t("q2_info"))

# ------------------------------ Q3 ----------------------------------------
with tabs[3]:
    st.subheader(t("q3_title"))
    st.caption(t("q3_caption"))
    c1, c2 = st.columns(2)
    sym = c1.slider(t("q3_symptom_w"), 0.0, 2.0, file_cfg.weights.symptom_fit, 0.1, key="q3_symptom")
    mp = c2.slider(t("q3_pref_w"), 0.0, 2.0, file_cfg.weights.mentor_pref, 0.1, key="q3_pref")
    st.slider(t("poor_fit"), 0.0, 1.0, file_cfg.thresholds.poor_fit_threshold, 0.05, key="q3_poor_fit")
    qf = st.session_state.get("q2_focus", file_cfg.weights.focus_overlap)
    qt = st.session_state.get("q2_trait", file_cfg.weights.trait_match)
    st.caption(t("q3_inherits", focus=qf, trait=qt))
    if st.button(t("run_q3"), type="primary", key="run_q3"):
        cfg = build_config(focus=qf, trait=qt, symptom=sym, mentor_pref=mp)
        st.session_state.q3 = (_match(cfg, cfg.engine), cfg, _match(cfg, "random"))
    if "q3" in st.session_state:
        res, cfg, base = st.session_state.q3
        show_metrics(res, cfg, baseline=base)
        ta, tb = st.tabs([t("assignments"), t("review_queue")])
        with ta:
            show_assignments(res, "q3")
        with tb:
            st.dataframe(pd.DataFrame(res.review_queue), use_container_width=True, height=360)
    else:
        st.info(t("q3_info"))

# ------------------------------ Q4 ----------------------------------------
with tabs[4]:
    st.subheader(t("q4_title"))
    st.caption(t("q4_caption"))
    c1, c2 = st.columns(2)
    c1.slider(t("reject_prob"), 0.0, 0.5, file_cfg.rejection_probability, 0.05, key="q4_reject")
    c2.number_input(t("seed"), value=file_cfg.random_seed, step=1, key="q4_seed")
    if st.button(t("run_q4"), type="primary", key="run_q4"):
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
        m[0].metric(t("rejected"), len(rr.rejected_ids))
        m[1].metric(t("mean_before"), f"{before['mean_score']:.3f}")
        m[2].metric(t("mean_after"), f"{after['mean_score']:.3f}",
                    f"{after['mean_score']-before['mean_score']:+.3f}")
        m[3].metric(t("coverage_after"), f"{after['coverage']*100:.1f}%")
        show_assignments(rr.final, "q4")
    else:
        st.info(t("q4_info"))
