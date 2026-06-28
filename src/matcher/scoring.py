"""Soft scoring for feasible (student, mentor) pairs.

Q2 (parent expectations) uses focus/trait overlap; Q3 (two-way fit) adds the
student's symptom needs and the mentor's own preference for the student. All
inputs are the structured tags produced by enrichment, so scoring is fully
deterministic and explainable.
"""
from __future__ import annotations

from typing import Dict

from .config import Weights

# Map a student's symptom category to the focus areas that would help it.
SYMPTOM_TO_FOCUS: Dict[str, set] = {
    "anxiety": {"stress-management", "emotional-support", "confidence"},
    "procrastination": {"time-management", "accountability", "motivation"},
    "low-motivation": {"motivation", "accountability"},
    "distraction": {"focus-attention", "study-habits"},
    "low-confidence": {"confidence", "emotional-support", "communication"},
    "social-difficulty": {"communication", "emotional-support"},
    "academic-pressure": {"stress-management", "study-habits", "exam-prep"},
    "emotional-difficulty": {"emotional-support", "stress-management"},
    "behavioral": {"accountability", "life-skills"},
    "none": set(),
}


def jaccard(a, b) -> float:
    sa, sb = set(a or []), set(b or [])
    if not sa and not sb:
        return 0.0
    union = sa | sb
    return len(sa & sb) / len(union) if union else 0.0


def coverage(needs, offered) -> float:
    """Fraction of `needs` covered by `offered` (asymmetric)."""
    sn = set(needs or [])
    if not sn:
        return 0.0
    return len(sn & set(offered or [])) / len(sn)


def score_pair(student_rec: dict, mentor_rec: dict, weights: Weights) -> dict:
    focus = jaccard(student_rec.get("desired_focus"), mentor_rec.get("offered_focus"))
    trait = jaccard(student_rec.get("desired_traits"), mentor_rec.get("personality_tags"))

    sym_needs = SYMPTOM_TO_FOCUS.get(student_rec.get("symptom_category", "none"), set())
    mentor_offer = set(mentor_rec.get("offered_focus", [])) | set(
        mentor_rec.get("preferred_student", {}).get("needs", []))
    symptom = coverage(sym_needs, mentor_offer)

    mentor_pref = coverage(mentor_rec.get("preferred_student", {}).get("needs"),
                           student_rec.get("desired_focus"))

    w = weights
    components = {
        "focus_overlap": (focus, w.focus_overlap),
        "trait_match": (trait, w.trait_match),
        "symptom_fit": (symptom, w.symptom_fit),
        "mentor_pref": (mentor_pref, w.mentor_pref),
    }
    wsum = sum(weight for _, weight in components.values()) or 1.0
    total = sum(val * weight for val, weight in components.values()) / wsum
    breakdown = {k: round(val, 4) for k, (val, _) in components.items()}
    breakdown["total"] = round(total, 4)
    return breakdown
