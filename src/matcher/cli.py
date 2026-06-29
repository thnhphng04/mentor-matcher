"""Command-line entry point.

    python -m matcher.cli enrich [--kind both|student|mentor] [--sync] [--sample N]
    python -m matcher.cli run    [--engine optimal|greedy|random]
    python -m matcher.cli rematch

Run with ``PYTHONPATH=src`` (or after ``pip install -e .``).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

from .config import ROOT, load_config, load_overrides
from .data_io import load_mentors, load_students
from . import enrich as enrich_mod
from .matcher import run_matching
from .metrics import baseline_delta, summarize
from .rematch import simulate_and_rematch

OUT = ROOT / "outputs"


def _api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


def cmd_enrich(args):
    cfg = load_config()
    students = load_students()
    mentors = load_mentors()
    model = cfg.enrichment.resolve_model()
    key = _api_key()

    def run_kind(kind, items):
        if not key:
            print(f"[{kind}] no OPENAI_API_KEY -> deterministic keyword cache")
            recs = {it.id: (enrich_mod.keyword_enrich_student(it) if kind == "student"
                            else enrich_mod.keyword_enrich_mentor(it)) for it in items}
        elif args.sync:
            print(f"[{kind}] sync enrichment via {model} ({len(items)} rows)")
            recs = enrich_mod.enrich_sync(items, kind, model, key, cfg.enrichment.max_workers,
                                          cfg.enrichment.max_retries,
                                          progress_cb=lambda d, t: print(f"  {d}/{t}", end="\r"))
            print()
        else:
            print(f"[{kind}] BATCH enrichment via {model} ({len(items)} rows) — polling...")
            recs = enrich_mod.enrich_batch(items, kind, model, key)
        enrich_mod.save_cache(cfg, kind, recs)
        print(f"[{kind}] wrote {len(recs)} records to {enrich_mod._cache_file(cfg, kind)}")

    if args.sample:
        students = students[:args.sample]
        mentors = mentors[:args.sample]
    if args.kind in ("both", "student"):
        run_kind("student", students)
    if args.kind in ("both", "mentor"):
        run_kind("mentor", mentors)


def _write_outputs(result, name):
    OUT.mkdir(exist_ok=True)
    pd.DataFrame(result.assignments).to_csv(OUT / f"{name}_assignments.csv", index=False)
    pd.DataFrame(result.unassigned).to_csv(OUT / f"{name}_unassigned.csv", index=False)
    pd.DataFrame(result.review_queue).to_csv(OUT / f"{name}_review_queue.csv", index=False)


def cmd_run(args):
    cfg = load_config()
    overrides = load_overrides()
    students = load_students()
    mentors = load_mentors()
    srecs, mrecs = enrich_mod.get_enrichment(students, mentors, cfg)

    engine = args.engine or cfg.engine
    result = run_matching(students, mentors, srecs, mrecs, cfg, overrides, engine=engine)
    baseline = run_matching(students, mentors, srecs, mrecs, cfg, overrides, engine="random")

    _write_outputs(result, "run")
    summary = summarize(result, len(students), cfg)
    delta = baseline_delta(result, baseline, len(students), cfg)
    print(json.dumps({"summary": summary, "vs_baseline": delta}, indent=2))
    print(f"\nWrote outputs to {OUT}")
    _assert_valid(result, students, mentors, srecs, cfg)


def cmd_rematch(args):
    cfg = load_config()
    overrides = load_overrides()
    students = load_students()
    mentors = load_mentors()
    srecs, mrecs = enrich_mod.get_enrichment(students, mentors, cfg)
    rr = simulate_and_rematch(students, mentors, srecs, mrecs, cfg, overrides)
    _write_outputs(rr.final, "rematch")
    before = summarize(rr.initial, len(students), cfg)
    after = summarize(rr.final, len(students), cfg)
    print(json.dumps({
        "rejected_count": len(rr.rejected_ids),
        "before": before,
        "after": after,
        "mean_score_change": round(after["mean_score"] - before["mean_score"], 4),
    }, indent=2))


def _assert_valid(result, students, mentors, srecs, cfg):
    """Sanity-check every matched row satisfies gender + a real assigned time."""
    s_by = {s.id: s for s in students}
    m_by = {m.id: m for m in mentors}
    bad = 0
    for a in result.assignments:
        if a["reason"] != "matched":
            continue
        m = m_by[a["mentor_id"]]
        req = srecs[a["student_id"]].get("requested_mentor_gender")
        if cfg.enforce_gender and req and m.gender != req:
            bad += 1
        if a["assigned_time"] == "n/a":
            bad += 1
    print(f"Validation: {bad} invalid matched rows (expected 0).")


def main(argv=None):
    p = argparse.ArgumentParser(prog="matcher")
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("enrich", help="run/refresh the LLM enrichment cache")
    pe.add_argument("--kind", choices=["both", "student", "mentor"], default="both")
    pe.add_argument("--sync", action="store_true", help="synchronous instead of Batch API")
    pe.add_argument("--sample", type=int, default=0, help="only enrich the first N of each")
    pe.set_defaults(func=cmd_enrich)

    pr = sub.add_parser("run", help="run the matcher and write outputs")
    pr.add_argument("--engine", choices=["optimal", "greedy", "random"], default=None)
    pr.set_defaults(func=cmd_run)

    prm = sub.add_parser("rematch", help="Q4 rejection + re-match simulation")
    prm.set_defaults(func=cmd_rematch)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
