from matcher.data_io import Mentor, Slot, Student, Window
from matcher.schedule import feasible_bookings, slot_fits_window


def w(day, start, end):
    return Window(day, start, end)


def test_exact_end_fits():
    # window 09:00-09:30, session 30 -> start 09:00 fits exactly.
    assert slot_fits_window(Slot("monday", 540), w("monday", 540, 570), 30)


def test_exceeds_end_fails():
    # start 09:10 + 30 = 09:40 > 09:30 end.
    assert not slot_fits_window(Slot("monday", 550), w("monday", 540, 570), 30)


def test_wrong_day_fails():
    assert not slot_fits_window(Slot("tuesday", 540), w("monday", 540, 570), 30)


def test_before_start_fails():
    assert not slot_fits_window(Slot("monday", 530), w("monday", 540, 570), 30)


def test_feasible_bookings_any_of():
    student = Student("s", "S", "Male",
                      [Slot("monday", 540), Slot("friday", 600)], "", "")
    mentor = Mentor("m", "M", "Female",
                    [w("friday", 600, 660)], "", "")
    bookings = feasible_bookings(student, mentor, 30)
    assert bookings == [("friday", 600)]
