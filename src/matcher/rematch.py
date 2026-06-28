"""Q4 — simulate rejection and re-match.

After an initial match, each *matched* student rejects their mentor with
``rejection_probability`` (seeded). Kept students are pinned to their mentor
(via force overrides) so they don't move; each rejected student's old mentor is
blocked, and the rejected pool is re-matched against the remaining capacity.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Set, Tuple

from .config import Config, Overrides, Pair
from .data_io import Mentor, Student
from .matcher import Result, run_matching


@dataclass
class RematchResult:
    initial: Result
    final: Result
    rejected_ids: List[str]


def simulate_and_rematch(students: List[Student], mentors: List[Mentor],
                         srecs, mrecs, cfg: Config, overrides: Overrides) -> RematchResult:
    initial = run_matching(students, mentors, srecs, mrecs, cfg, overrides, engine="optimal")

    rng = random.Random(cfg.random_seed)
    matched = [a for a in initial.assignments if a["reason"] == "matched"]
    rejected = [a for a in matched if rng.random() < cfg.rejection_probability]
    rejected_ids = [a["student_id"] for a in rejected]
    rejected_pairs: Set[Tuple[str, str]] = {(a["student_id"], a["mentor_id"]) for a in rejected}

    # Pin everyone who did NOT reject (matched-and-kept + forced) to their mentor.
    kept = [a for a in initial.assignments
            if a["student_id"] not in set(rejected_ids)
            and a["reason"] in ("matched", "forced")]
    new_overrides = overrides.model_copy(deep=True)
    new_overrides.force = list(new_overrides.force) + [
        Pair(student_id=a["student_id"], mentor_id=a["mentor_id"]) for a in kept]

    final = run_matching(students, mentors, srecs, mrecs, cfg, new_overrides,
                         engine="optimal", blocked_extra=rejected_pairs)
    return RematchResult(initial=initial, final=final, rejected_ids=rejected_ids)
