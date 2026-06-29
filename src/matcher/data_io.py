"""Load the mentor/student CSVs and parse their JSON schedule columns."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd

from .config import ROOT

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def to_minutes(hhmm: str) -> int:
    """'17:30' -> 1050."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def to_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Window:
    day: str
    start: int   # minutes from midnight
    end: int


@dataclass
class Slot:
    day: str
    start: int


@dataclass
class Mentor:
    id: str
    name: str
    gender: str          # "Male" / "Female"
    windows: List[Window]
    personalites: str
    expectation: str


@dataclass
class Student:
    id: str
    name: str
    gender: str
    slots: List[Slot]
    symptom: str
    expectation: str


def _parse_mentor_capacity(raw: str) -> List[Window]:
    windows: List[Window] = []
    for day_block in json.loads(raw):
        day = day_block["day"].lower()
        for sl in day_block.get("slots", []):
            windows.append(Window(day, to_minutes(sl["start_time"]), to_minutes(sl["end_time"])))
    return windows


def _parse_student_slots(raw: str) -> List[Slot]:
    return [Slot(s["day"].lower(), to_minutes(s["start_time"])) for s in json.loads(raw)]


MENTOR_COLUMNS = ["ID", "Name", "gender", "capacity", "personalites", "expectation"]
STUDENT_COLUMNS = ["ID", "Name", "gender", "learning_slot", "symptom", "expectation"]


def validate_columns(df: pd.DataFrame, required: List[str]) -> List[str]:
    """Return the list of required columns missing from ``df`` (empty == valid)."""
    return [c for c in required if c not in df.columns]


def mentors_from_df(df: pd.DataFrame) -> List[Mentor]:
    out: List[Mentor] = []
    for _, r in df.iterrows():
        out.append(Mentor(
            id=str(r["ID"]),
            name=str(r["Name"]),
            gender=str(r["gender"]).strip().capitalize(),
            windows=_parse_mentor_capacity(r["capacity"]),
            personalites=str(r.get("personalites", "") or ""),
            expectation=str(r.get("expectation", "") or ""),
        ))
    return out


def students_from_df(df: pd.DataFrame) -> List[Student]:
    out: List[Student] = []
    for _, r in df.iterrows():
        out.append(Student(
            id=str(r["ID"]),
            name=str(r["Name"]),
            gender=str(r["gender"]).strip().capitalize(),
            slots=_parse_student_slots(r["learning_slot"]),
            symptom=str(r.get("symptom", "") or ""),
            expectation=str(r.get("expectation", "") or ""),
        ))
    return out


def load_mentors(path: str | Path | None = None) -> List[Mentor]:
    path = path if path is not None else ROOT / "data" / "mentors_prod_200_enriched.csv"
    return mentors_from_df(pd.read_csv(path))


def load_students(path: str | Path | None = None) -> List[Student]:
    path = path if path is not None else ROOT / "data" / "students_prod_2000_enriched.csv"
    return students_from_df(pd.read_csv(path))
