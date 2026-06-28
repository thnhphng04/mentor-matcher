from matcher.capacity import Booker, mentor_capacity
from matcher.data_io import Mentor, Window


def test_capacity_counts_blocks():
    # 09:00-10:00 = 60 min -> two 30-min blocks; 14:00-14:30 -> one block.
    m = Mentor("m", "M", "Female",
               [Window("monday", 540, 600), Window("monday", 840, 870)], "", "")
    assert mentor_capacity(m, 30, None) == 3
    assert mentor_capacity(m, 30, 2) == 2  # cap applies


def test_booker_rejects_overlap():
    b = Booker(30)
    assert b.book("m", [("monday", 540)]) == ("monday", 540)
    # 09:10 overlaps the 09:00-09:30 booking.
    assert b.book("m", [("monday", 550)]) is None
    assert b.count("m") == 1


def test_booker_allows_nonoverlapping():
    b = Booker(30)
    assert b.book("m", [("monday", 540)]) == ("monday", 540)
    assert b.book("m", [("monday", 570)]) == ("monday", 570)  # 09:30, adjacent, no overlap
    assert b.count("m") == 2


def test_booker_per_mentor_isolation():
    b = Booker(30)
    assert b.book("m1", [("monday", 540)]) == ("monday", 540)
    assert b.book("m2", [("monday", 540)]) == ("monday", 540)  # different mentor, fine
