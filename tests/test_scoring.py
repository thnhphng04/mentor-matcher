from matcher.config import Weights
from matcher.scoring import coverage, jaccard, score_pair


def test_jaccard():
    assert jaccard(["a", "b"], ["b", "c"]) == 1 / 3
    assert jaccard([], []) == 0.0
    assert jaccard(["a"], ["a"]) == 1.0


def test_coverage_asymmetric():
    assert coverage(["a", "b"], ["a"]) == 0.5
    assert coverage([], ["a"]) == 0.0


def test_score_pair_breakdown_and_range():
    student = {
        "desired_focus": ["time-management", "study-habits"],
        "desired_traits": ["patient"],
        "symptom_category": "procrastination",
    }
    mentor = {
        "offered_focus": ["time-management", "accountability"],
        "personality_tags": ["patient", "calm"],
        "preferred_student": {"grade_band": None, "needs": ["time-management"]},
    }
    bd = score_pair(student, mentor, Weights())
    assert set(bd) >= {"focus_overlap", "trait_match", "symptom_fit", "mentor_pref", "total"}
    assert 0.0 <= bd["total"] <= 1.0
    assert bd["focus_overlap"] > 0  # they share time-management


def test_score_zero_when_disjoint():
    student = {"desired_focus": ["confidence"], "desired_traits": [], "symptom_category": "none"}
    mentor = {"offered_focus": ["exam-prep"], "personality_tags": [],
              "preferred_student": {"grade_band": None, "needs": []}}
    assert score_pair(student, mentor, Weights())["total"] == 0.0
