"""Time feasibility between a student's desired slots and a mentor's windows.

A student wants ONE weekly session; their 1-3 ``learning_slot`` entries are
acceptable alternatives (any-of). A (student, mentor) pair is time-feasible if
any student slot starts inside any mentor window on the same day with room for
a session of ``session_length`` minutes.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from .data_io import Mentor, Slot, Student, Window


def slot_fits_window(slot: Slot, window: Window, session_length: int) -> bool:
    return (slot.day == window.day
            and slot.start >= window.start
            and slot.start + session_length <= window.end)


def feasible_bookings(student: Student, mentor: Mentor, session_length: int
                      ) -> List[Tuple[str, int]]:
    """All concrete (day, start_minute) blocks at which this pair could meet."""
    out: List[Tuple[str, int]] = []
    for slot in student.slots:
        for w in mentor.windows:
            if slot_fits_window(slot, w, session_length):
                out.append((slot.day, slot.start))
    # De-duplicate while preserving order.
    seen = set()
    uniq = []
    for b in out:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def first_booking(student: Student, mentor: Mentor, session_length: int
                  ) -> Optional[Tuple[str, int]]:
    bookings = feasible_bookings(student, mentor, session_length)
    return bookings[0] if bookings else None
