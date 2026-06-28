"""Match-quality metrics and baseline comparison."""
from __future__ import annotations

import statistics
from typing import Dict

from .config import Config
from .matcher import Result


def summarize(result: Result, total_students: int, cfg: Config) -> Dict:
    matched = [a for a in result.assignments]
    scores = [a["total_score"] for a in matched]
    min_acc = cfg.thresholds.min_acceptable_score
    n_matched = len(matched)
    return {
        "engine": result.engine,
        "total_students": total_students,
        "matched": n_matched,
        "unassigned": total_students - n_matched,
        "coverage": round(n_matched / total_students, 4) if total_students else 0.0,
        "mean_score": round(statistics.mean(scores), 4) if scores else 0.0,
        "median_score": round(statistics.median(scores), 4) if scores else 0.0,
        "pct_above_min_acceptable": round(
            sum(s >= min_acc for s in scores) / n_matched, 4) if n_matched else 0.0,
        "review_queue_size": len(result.review_queue),
    }


def baseline_delta(result: Result, baseline: Result, total_students: int, cfg: Config) -> Dict:
    r = summarize(result, total_students, cfg)
    b = summarize(baseline, total_students, cfg)
    return {
        "engine": r["engine"],
        "baseline_engine": b["engine"],
        "mean_score": r["mean_score"],
        "baseline_mean_score": b["mean_score"],
        "mean_score_delta": round(r["mean_score"] - b["mean_score"], 4),
        "coverage": r["coverage"],
        "baseline_coverage": b["coverage"],
    }
