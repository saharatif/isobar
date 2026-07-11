"""SQLAlchemy models — mirrors the Postgres schema in ARCHITECTURE-BACKEND.md §3.

v0.1 deltas from the target schema: SQLite instead of Postgres, embeddings
stored as JSON arrays instead of pgvector, no org/user tenancy yet (single
tenant per the roadmap).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    file_key: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(Integer)
    # uploaded | parsing | parsed | failed
    status: Mapped[str] = mapped_column(String(20), default="uploaded")
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id"))
    name: Mapped[str | None] = mapped_column(String(255), default=None)
    current_title: Mapped[str | None] = mapped_column(String(255), default=None)
    years_exp: Mapped[int | None] = mapped_column(Integer, default=None)
    # junior | mid | senior | staff | principal
    seniority: Mapped[str | None] = mapped_column(String(20), default=None)
    signal_score: Mapped[int | None] = mapped_column(Integer, default=None)
    embedding: Mapped[list | None] = mapped_column(JSON, default=None)
    # parsing | matched | failed
    status: Mapped[str] = mapped_column(String(20), default="parsing")
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=_now)

    skills: Mapped[list["CandidateSkill"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )
    domains: Mapped[list["CandidateDomain"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )
    matches: Mapped[list["Match"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"), primary_key=True
    )
    skill: Mapped[str] = mapped_column(String(100), primary_key=True)
    weight: Mapped[float] = mapped_column(Float)


class CandidateDomain(Base):
    __tablename__ = "candidate_domains"

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"), primary_key=True
    )
    domain: Mapped[str] = mapped_column(String(100), primary_key=True)
    weight: Mapped[float] = mapped_column(Float)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source: Mapped[str] = mapped_column(String(50), default="seed")
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255), default=None)
    city: Mapped[str | None] = mapped_column(String(100), default=None)
    country_code: Mapped[str | None] = mapped_column(String(2), default=None)
    lat: Mapped[float | None] = mapped_column(Float, default=None)
    lon: Mapped[float | None] = mapped_column(Float, default=None)
    seniority: Mapped[str | None] = mapped_column(String(20), default=None)
    comp_min: Mapped[int | None] = mapped_column(Integer, default=None)
    comp_max: Mapped[int | None] = mapped_column(Integer, default=None)
    currency: Mapped[str | None] = mapped_column(String(3), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    embedding: Mapped[list | None] = mapped_column(JSON, default=None)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Match(Base):
    __tablename__ = "matches"

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"), primary_key=True
    )
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    score: Mapped[float] = mapped_column(Float)

    job: Mapped[Job] = relationship(lazy="selectin")
