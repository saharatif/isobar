"""Pydantic schema for structured résumé extraction (LLM output contract).

Weights are clamped, not rejected: LLM output occasionally drifts slightly out
of range and a résumé pipeline should degrade gracefully rather than 500.
"""
from typing import Literal

from pydantic import BaseModel, field_validator

Seniority = Literal["junior", "mid", "senior", "staff", "principal"]


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


class SkillItem(BaseModel):
    name: str
    weight: float = 0.5  # 0..1

    @field_validator("weight")
    @classmethod
    def _weight_range(cls, v: float) -> float:
        return _clamp01(v)


class DomainItem(BaseModel):
    name: str  # cloud | ml | backend | data | devops | product | ...
    weight: float = 0.0  # 0..1, all domains sum to ~1

    @field_validator("weight")
    @classmethod
    def _weight_range(cls, v: float) -> float:
        return _clamp01(v)


class RoleItem(BaseModel):
    company: str | None = None
    title: str | None = None
    start: str | None = None  # e.g. "2021-03"
    end: str | None = None  # None or "present" means current role


class Extraction(BaseModel):
    name: str | None = None
    current_title: str | None = None
    years_experience: int | None = None
    seniority: Seniority | None = None
    skills: list[SkillItem] = []
    domains: list[DomainItem] = []
    roles: list[RoleItem] = []

    @field_validator("years_experience")
    @classmethod
    def _years_range(cls, v: int | None) -> int | None:
        if v is None:
            return None
        return max(0, min(60, v))
