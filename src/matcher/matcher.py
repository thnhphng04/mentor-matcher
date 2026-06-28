"""The assignment engine.

Three engines share one code path:
  * ``greedy``  — highest-score-first; the explainable Q2 baseline reference.
  * ``optimal`` — min-cost max-flow (coverage first, then total score).
  * ``random``  — seeded random feasible assignment; the naive baseline.

Manual overrides are honoured: ``force`` pairs are pre-booked, ``block``/``skip``
are applied while building feasibility (see constraints.py).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx

from .capacity import Booker, mentor_capacity
from .config import Config, Overrides
from .constraints import Edge, Feasibility, build_feasibility
from .data_io import Mentor, Student, to_hhmm
from .scoring import score_pair

SCALE = 1000  # float score -> integer edge cost for the flow solver


@dataclass
class Result:
    assignments: List[dict] = field(default_factory=list)   # one row per matched student
    unassigned: List[dict] = field(default_factory=list)    # {student_id, reason}
    review_queue: List[dict] = field(default_factory=list)   # poor-fit assignments
    engine: str = ""

    @property
    def mean_score(self) -> float:
        if not self.assignments:
            return 0.0
        return sum(a["total_score"] for a in self.assignments) / len(self.assignments)


def _score_edges(student_ids, edges: Dict[str, List[Edge]],
                 srecs, mrecs, weights) -> Dict[Tuple[str, str], dict]:
    """Pre-compute score breakdowns for every feasible edge."""
    scores: Dict[Tuple[str, str], dict] = {}
    for sid in student_ids:
        for e in edges.get(sid, []):
            scores[(sid, e.mentor_id)] = score_pair(srecs[sid], mrecs[e.mentor_id], weights)
    return scores


def _greedy(student_ids, edges, scores, remaining_cap) -> Dict[str, str]:
    """Highest score first; assign if mentor has remaining capacity."""
    triples = []
    for sid in student_ids:
        for e in edges.get(sid, []):
            triples.append((scores[(sid, e.mentor_id)]["total"], sid, e.mentor_id))
    triples.sort(reverse=True)
    assigned: Dict[str, str] = {}
    for _, sid, mid in triples:
        if sid in assigned:
            continue
        if remaining_cap.get(mid, 0) <= 0:
            continue
        assigned[sid] = mid
        remaining_cap[mid] -= 1
    return assigned


def _random(student_ids, edges, remaining_cap, seed) -> Dict[str, str]:
    rng = random.Random(seed)
    order = list(student_ids)
    rng.shuffle(order)
    assigned: Dict[str, str] = {}
    for sid in order:
        options = [e.mentor_id for e in edges.get(sid, []) if remaining_cap.get(e.mentor_id, 0) > 0]
        if options:
            mid = rng.choice(options)
            assigned[sid] = mid
            remaining_cap[mid] -= 1
    return assigned


def _optimal(student_ids, edges, scores, remaining_cap) -> Dict[str, str]:
    """Min-cost max-flow: maximise coverage, then total score."""
    g = nx.DiGraph()
    g.add_node("S")
    g.add_node("T")
    used_students = []
    for sid in student_ids:
        opts = [e for e in edges.get(sid, []) if remaining_cap.get(e.mentor_id, 0) > 0]
        if not opts:
            continue
        used_students.append(sid)
        snode = f"s::{sid}"
        g.add_edge("S", snode, capacity=1, weight=0)
        for e in opts:
            mnode = f"m::{e.mentor_id}"
            cost = -int(round(scores[(sid, e.mentor_id)]["total"] * SCALE))
            g.add_edge(snode, mnode, capacity=1, weight=cost)
    for mid, cap in remaining_cap.items():
        if cap > 0:
            g.add_edge(f"m::{mid}", "T", capacity=cap, weight=0)
    if not used_students:
        return {}
    flow = nx.max_flow_min_cost(g, "S", "T")
    assigned: Dict[str, str] = {}
    for sid in used_students:
        snode = f"s::{sid}"
        for mnode, f in flow.get(snode, {}).items():
            if f > 0 and mnode.startswith("m::"):
                assigned[sid] = mnode[3:]
                break
    return assigned


def run_matching(students: List[Student], mentors: List[Mentor],
                 srecs: Dict[str, dict], mrecs: Dict[str, dict],
                 cfg: Config, overrides: Overrides,
                 engine: Optional[str] = None,
                 blocked_extra: Optional[set] = None) -> Result:
    """Full matching pass. ``blocked_extra`` adds (student_id, mentor_id) pairs to
    forbid (used by Q4 re-matching to bar a rejected mentor)."""
    engine = engine or cfg.engine
    mentors_by_id = {m.id: m for m in mentors}
    students_by_id = {s.id: s for s in students}

    # Merge runtime-blocked pairs (e.g. Q4 rejections) into the overrides view.
    if blocked_extra:
        ov = overrides.model_copy(deep=True)
        from .config import Pair
        ov.block = list(ov.block) + [Pair(student_id=a, mentor_id=b) for (a, b) in blocked_extra]
        overrides = ov

    feas = build_feasibility(students, mentors, srecs, cfg, overrides)
    booker = Booker(cfg.session_length_minutes)
    result = Result(engine=engine)

    # 1. Forced pairs first — pre-book, consuming capacity.
    forced_students = set()
    cap = {m.id: mentor_capacity(m, cfg.session_length_minutes, cfg.max_students_per_mentor)
           for m in mentors if m.id not in set(overrides.skip_mentors)}
    for p in overrides.force:
        s = students_by_id.get(p.student_id)
        m = mentors_by_id.get(p.mentor_id)
        if not s or not m:
            continue
        from .schedule import feasible_bookings
        blocks = feasible_bookings(s, m, cfg.session_length_minutes) or [(s.slots[0].day, s.slots[0].start)] if s.slots else []
        booking = booker.book(m.id, blocks) if blocks else None
        day, start = booking if booking else ("n/a", -1)
        bd = score_pair(srecs[s.id], mrecs[m.id], cfg.weights) if m.id in mrecs else {"total": 0.0}
        result.assignments.append(_row(s, m, day, start, bd, "forced"))
        forced_students.add(s.id)
        cap[m.id] = max(0, cap.get(m.id, 0) - 1)

    # 2. Score feasible edges for the remaining students.
    pool = [sid for sid in feas.edges if sid not in forced_students]
    scores = _score_edges(pool, feas.edges, srecs, mrecs, cfg.weights)
    remaining_cap = dict(cap)

    # 3. Run the chosen engine -> tentative student->mentor map.
    if engine == "greedy":
        tentative = _greedy(pool, feas.edges, scores, remaining_cap)
    elif engine == "random":
        tentative = _random(pool, feas.edges, remaining_cap, cfg.random_seed)
    else:
        tentative = _optimal(pool, feas.edges, scores, remaining_cap)

    # 4. Book concrete, non-overlapping blocks (highest score first).
    edge_blocks = {(sid, e.mentor_id): e.blocks for sid in pool for e in feas.edges[sid]}
    edges_by_student = {sid: sorted(feas.edges[sid],
                                    key=lambda e: scores[(sid, e.mentor_id)]["total"], reverse=True)
                        for sid in pool}
    ordered = sorted(tentative.items(),
                     key=lambda kv: scores[(kv[0], kv[1])]["total"], reverse=True)
    assigned_ids = set()
    for sid, mid in ordered:
        booking = booker.book(mid, edge_blocks[(sid, mid)])
        if booking is None:
            continue  # repaired below
        day, start = booking
        result.assignments.append(
            _row(students_by_id[sid], mentors_by_id[mid], day, start, scores[(sid, mid)], "matched"))
        assigned_ids.add(sid)

    # 5. Repair pass — students dropped by booking conflicts or left out by the
    # engine get re-tried on their next-best feasible mentor with free capacity.
    leftover = [sid for sid in pool if sid not in assigned_ids]
    leftover.sort(key=lambda s: edges_by_student[s][0] and scores[(s, edges_by_student[s][0].mentor_id)]["total"],
                  reverse=True)
    for sid in leftover:
        placed = False
        for e in edges_by_student[sid]:
            mid = e.mentor_id
            if booker.count(mid) >= cap.get(mid, 0):
                continue
            booking = booker.book(mid, e.blocks)
            if booking is None:
                continue
            day, start = booking
            result.assignments.append(
                _row(students_by_id[sid], mentors_by_id[mid], day, start, scores[(sid, mid)], "matched"))
            assigned_ids.add(sid)
            placed = True
            break
        if not placed:
            result.unassigned.append({"student_id": sid, "reason": "no remaining mentor capacity"})

    # 6. Hard-infeasible + skipped.
    for sid, reason in feas.unassignable.items():
        result.unassigned.append({"student_id": sid, "reason": reason})
    for sid in feas.skipped_students:
        result.unassigned.append({"student_id": sid, "reason": "skipped by override"})

    # 7. Poor-fit review queue.
    thr = cfg.thresholds.poor_fit_threshold
    result.review_queue = [a for a in result.assignments
                           if a["reason"] == "matched" and a["total_score"] < thr]
    return result


def _row(student: Student, mentor: Mentor, day: str, start: int, breakdown: dict, reason: str) -> dict:
    return {
        "student_id": student.id,
        "student_name": student.name,
        "mentor_id": mentor.id,
        "mentor_name": mentor.name,
        "assigned_day": day,
        "assigned_time": to_hhmm(start) if start >= 0 else "n/a",
        "total_score": breakdown.get("total", 0.0),
        "focus_overlap": breakdown.get("focus_overlap", 0.0),
        "trait_match": breakdown.get("trait_match", 0.0),
        "symptom_fit": breakdown.get("symptom_fit", 0.0),
        "mentor_pref": breakdown.get("mentor_pref", 0.0),
        "reason": reason,
    }
