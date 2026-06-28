"""Mentor capacity model.

The ``capacity`` CSV column is actually an availability schedule, so we *define*
capacity as the number of non-overlapping session-length blocks that fit across
a mentor's windows, optionally bounded by ``max_students_per_mentor``.

At assignment time the :class:`Booker` places each student into a concrete
(day, start) block that does not overlap another student already booked with the
same mentor — so no two students share a time.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .data_io import Mentor


def mentor_capacity(mentor: Mentor, session_length: int, max_cap: Optional[int]) -> int:
    blocks = sum((w.end - w.start) // session_length for w in mentor.windows)
    if max_cap is not None:
        blocks = min(blocks, max_cap)
    return blocks


class Booker:
    """Tracks concrete bookings per mentor and enforces non-overlap."""

    def __init__(self, session_length: int):
        self.session_length = session_length
        self._booked: Dict[str, List[Tuple[str, int, int]]] = {}

    def _overlaps(self, mentor_id: str, day: str, start: int) -> bool:
        end = start + self.session_length
        for (d, s, e) in self._booked.get(mentor_id, []):
            if d == day and start < e and s < end:
                return True
        return False

    def book(self, mentor_id: str, feasible_blocks: List[Tuple[str, int]]
             ) -> Optional[Tuple[str, int]]:
        """Reserve the first non-conflicting block; return it or None."""
        for (day, start) in feasible_blocks:
            if not self._overlaps(mentor_id, day, start):
                self._booked.setdefault(mentor_id, []).append(
                    (day, start, start + self.session_length))
                return (day, start)
        return None

    def count(self, mentor_id: str) -> int:
        return len(self._booked.get(mentor_id, []))
