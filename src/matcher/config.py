"""Configuration and override loading.

All tunable behaviour lives in ``config.yaml`` and ``overrides.yaml`` so the
interviewer can change rules, weights, and manual pairings without editing code.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

# Project root = two levels up from this file (src/matcher/config.py -> project).
ROOT = Path(__file__).resolve().parents[2]


class Weights(BaseModel):
    focus_overlap: float = 1.0
    trait_match: float = 0.6
    symptom_fit: float = 0.8
    mentor_pref: float = 0.6


class Thresholds(BaseModel):
    min_acceptable_score: float = 0.30
    poor_fit_threshold: float = 0.15


class Enrichment(BaseModel):
    provider: str = "openai"
    model_env: str = "OPENAI_MODEL"
    default_model: str = "gpt-4o-mini"
    use_batch: bool = True
    cache_dir: str = "data/cache"
    max_workers: int = 8
    max_retries: int = 2          # extra LLM attempts per row before keyword fallback

    def resolve_model(self) -> str:
        return os.environ.get(self.model_env) or self.default_model


class Config(BaseModel):
    session_length_minutes: int = 30
    max_students_per_mentor: Optional[int] = 12
    enforce_gender: bool = True
    weights: Weights = Field(default_factory=Weights)
    thresholds: Thresholds = Field(default_factory=Thresholds)
    rejection_probability: float = 0.20
    random_seed: int = 42
    engine: str = "optimal"
    enrichment: Enrichment = Field(default_factory=Enrichment)

    @property
    def cache_path(self) -> Path:
        return (ROOT / self.enrichment.cache_dir).resolve()


class Pair(BaseModel):
    student_id: str
    mentor_id: str


class Overrides(BaseModel):
    force: List[Pair] = Field(default_factory=list)
    block: List[Pair] = Field(default_factory=list)
    skip_students: List[str] = Field(default_factory=list)
    skip_mentors: List[str] = Field(default_factory=list)

    @property
    def blocked_set(self) -> set[tuple[str, str]]:
        return {(p.student_id, p.mentor_id) for p in self.block}


def load_config(path: str | Path | None = None) -> Config:
    path = Path(path) if path else ROOT / "config.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Config(**data)


def load_overrides(path: str | Path | None = None) -> Overrides:
    path = Path(path) if path else ROOT / "overrides.yaml"
    if not path.exists():
        return Overrides()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # Treat explicit nulls (empty YAML keys) as empty lists.
    data = {k: (v if v is not None else []) for k, v in data.items()}
    return Overrides(**data)
