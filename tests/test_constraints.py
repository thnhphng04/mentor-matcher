from matcher.config import Config, Overrides
from matcher.constraints import build_feasibility, gender_ok
from matcher.data_io import Mentor, Slot, Student, Window
from matcher.enrich import extract_requested_gender


def _student(sid, gender, slots, expectation=""):
    return Student(sid, sid, gender, slots, "", expectation)


def _mentor(mid, gender):
    return Mentor(mid, mid, gender, [Window("monday", 540, 600)], "", "")


def test_gender_enforced_only_when_requested():
    male_mentor = _mentor("m", "Male")
    assert gender_ok({"requested_mentor_gender": None}, male_mentor, True)      # unstated -> ok
    assert gender_ok({"requested_mentor_gender": "Male"}, male_mentor, True)    # match -> ok
    assert not gender_ok({"requested_mentor_gender": "Female"}, male_mentor, True)  # mismatch


def test_opposite_gender_request_honoured():
    # Female student whose parent requests a Male mentor.
    g = extract_requested_gender("Parent prefers a Male mentor so she opens up", "Female")
    assert g == "Male"


def test_same_gender_phrase_uses_student_gender():
    g = extract_requested_gender("Gia đình đề nghị mentor cùng giới", "Female")
    assert g == "Female"


def test_build_feasibility_blocks_and_unassignable():
    s = _student("s", "Male", [Slot("monday", 540)])
    m = _mentor("m", "Female")
    recs = {"s": {"requested_mentor_gender": "Male"}}  # requests Male, only Female mentor exists
    cfg = Config()
    feas = build_feasibility([s], [m], recs, cfg, Overrides())
    assert "s" in feas.unassignable
    assert "gender" in feas.unassignable["s"]


def test_skip_student_excluded():
    s = _student("s", "Male", [Slot("monday", 540)])
    m = _mentor("m", "Male")
    recs = {"s": {"requested_mentor_gender": None}}
    feas = build_feasibility([s], [m], recs, Config(), Overrides(skip_students=["s"]))
    assert "s" in feas.skipped_students
    assert "s" not in feas.edges
