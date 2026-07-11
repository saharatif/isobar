"""API request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class UploadOut(BaseModel):
    file_key: str
    filename: str
    size_bytes: int
    mime_type: str


class CandidateCreate(BaseModel):
    file_key: str = Field(min_length=1, max_length=255)
    filename: str = Field(default="resume", max_length=255)
    mime_type: str = Field(max_length=255)


class SkillOut(BaseModel):
    name: str
    weight: float


class DomainOut(BaseModel):
    name: str
    weight: float


class CandidateOut(BaseModel):
    id: str
    status: str
    name: str | None
    current_title: str | None
    years_exp: int | None
    seniority: str | None
    signal_score: int | None
    created_at: datetime


class HotspotOut(BaseModel):
    city: str
    country_code: str | None
    lat: float | None
    lon: float | None
    demand_score: int
    open_roles: int


class OpportunityOut(BaseModel):
    job_id: str
    title: str
    company: str | None
    city: str | None
    country_code: str | None
    seniority: str | None
    comp_min: int | None
    comp_max: int | None
    currency: str | None
    match_pct: int


class SnapshotOut(BaseModel):
    candidate: CandidateOut
    skills: list[SkillOut]
    domains: list[DomainOut]
    hotspots: list[HotspotOut]
    opportunities: list[OpportunityOut]
    markets_matched: int
