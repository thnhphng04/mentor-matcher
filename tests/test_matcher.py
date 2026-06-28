from matcher.config import Config, Overrides, Pair
from matcher.constraints import Edge
from matcher.data_io import Mentor, Slot, Student, Window
from matcher.matcher import _greedy, _optimal, run_matching


# ----- engine comparison: optimal beats greedy on a designed case -----
def _setup_engine_case():
    edges = {
        "s1": [Edge("m1", [("monday", 540)]), Edge("m2", [("monday", 540)])],
        "s2": [Edge("m1", [("monday", 540)]), Edge("m2", [("monday", 540)])],
    }
    scores = {
        ("s1", "m1"): {"total": 0.90}, ("s1", "m2"): {"total": 0.50},
        ("s2", "m1"): {"total": 0.85}, ("s2", "m2"): {"total": 0.00},
    }
    return edges, scores


def _total(assign, scores):
    return sum(scores[(s, m)]["total"] for s, m in assign.items())


def test_optimal_beats_greedy():
    edges, scores = _setup_engine_case()
    greedy = _greedy(["s1", "s2"], edges, scores, {"m1": 1, "m2": 1})
    optimal = _optimal(["s1", "s2"], edges, scores, {"m1": 1, "m2": 1})
    assert _total(greedy, scores) == 0.90      # greedy grabs s1->m1, strands s2
    assert _total(optimal, scores) == 1.35      # optimal: s1->m2 + s2->m1
    assert _total(optimal, scores) > _total(greedy, scores)


# ----- overrides through the full run_matching path -----
def _world():
    win = [Window("monday", 540, 600)]
    students = [Student("s1", "s1", "Male", [Slot("monday", 540)], "", ""),
                Student("s2", "s2", "Male", [Slot("monday", 540)], "", "")]
    mentors = [Mentor("m1", "m1", "Male", win, "", ""),
               Mentor("m2", "m2", "Male", win, "", "")]
    rec_s = {"requested_mentor_gender": None, "desired_focus": ["study-habits"],
             "desired_traits": [], "symptom_category": "none"}
    rec_m = {"offered_focus": ["study-habits"], "personality_tags": [],
             "preferred_student": {"grade_band": None, "needs": []}}
    srecs = {"s1": dict(rec_s), "s2": dict(rec_s)}
    mrecs = {"m1": dict(rec_m), "m2": dict(rec_m)}
    return students, mentors, srecs, mrecs


def test_force_override():
    students, mentors, srecs, mrecs = _world()
    ov = Overrides(force=[Pair(student_id="s1", mentor_id="m2")])
    res = run_matching(students, mentors, srecs, mrecs, Config(), ov, engine="optimal")
    forced = [a for a in res.assignments if a["student_id"] == "s1"]
    assert forced and forced[0]["mentor_id"] == "m2" and forced[0]["reason"] == "forced"


def test_block_override():
    students, mentors, srecs, mrecs = _world()
    ov = Overrides(block=[Pair(student_id="s1", mentor_id="m1")])
    res = run_matching(students, mentors, srecs, mrecs, Config(), ov, engine="optimal")
    pairs = {(a["student_id"], a["mentor_id"]) for a in res.assignments}
    assert ("s1", "m1") not in pairs


def test_skip_student():
    students, mentors, srecs, mrecs = _world()
    ov = Overrides(skip_students=["s2"])
    res = run_matching(students, mentors, srecs, mrecs, Config(), ov, engine="optimal")
    assert "s2" not in {a["student_id"] for a in res.assignments}
    assert any(u["student_id"] == "s2" and "skip" in u["reason"] for u in res.unassigned)
