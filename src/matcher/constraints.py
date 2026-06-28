"""Build the feasible edge set under the Q1 hard constraints.

Hard constraints:
  * gender  — if the parent requested a mentor gender, the mentor must match.
  * time    — at least one student slot must fit a mentor window.
Plus interviewer overrides (block / skip) are applied here.

An edge carries the concrete feasible (day, start) blocks so the booker can
place a non-overlapping session later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .config import Config, Overrides
from .data_io import Mentor, Student
from .schedule import feasible_bookings


@dataclass
class Edge:
    mentor_id: str
    blocks: List[Tuple[str, int]]


@dataclass
class Feasibility:
    edges: Dict[str, List[Edge]]            # student_id -> feasible edges
    unassignable: Dict[str, str]            # student_id -> reason (no feasible mentor)
    skipped_students: List[str] = field(default_factory=list)


def gender_ok(student_rec: dict, mentor: Mentor, enforce: bool) -> bool:
    if not enforce:
        return True
    req = student_rec.get("requested_mentor_gender")
    if not req:
        return True
    return mentor.gender == req


def build_feasibility(students: List[Student], mentors: List[Mentor],
                      student_recs: Dict[str, dict], cfg: Config,
                      overrides: Overrides) -> Feasibility:
    skip_students = set(overrides.skip_students)
    skip_mentors = set(overrides.skip_mentors)
    blocked = overrides.blocked_set
    active_mentors = [m for m in mentors if m.id not in skip_mentors]

    edges: Dict[str, List[Edge]] = {}
    unassignable: Dict[str, str] = {}
    skipped: List[str] = []
    sl = cfg.session_length_minutes

    for s in students:
        if s.id in skip_students:
            skipped.append(s.id)
            continue
        srec = student_recs[s.id]
        any_gender = False
        any_time = False
        s_edges: List[Edge] = []
        for m in active_mentors:
            if (s.id, m.id) in blocked:
                continue
            g = gender_ok(srec, m, cfg.enforce_gender)
            if g:
                any_gender = True
            blocks = feasible_bookings(s, m, sl)
            if blocks:
                any_time = True
            if g and blocks:
                s_edges.append(Edge(m.id, blocks))
        if s_edges:
            edges[s.id] = s_edges
        else:
            if not any_gender:
                unassignable[s.id] = "no mentor of the requested gender"
            elif not any_time:
                unassignable[s.id] = "no mentor with an overlapping time slot"
            else:
                unassignable[s.id] = "no mentor satisfying both gender and time"
    return Feasibility(edges=edges, unassignable=unassignable, skipped_students=skipped)
