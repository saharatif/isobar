"""Candidate endpoints — create (runs the sync pipeline), read, snapshot, delete."""
import logging
import math
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALLOWED_MIME_TYPES, Settings
from app.deps import get_extractor, get_session, get_settings
from app.models import Candidate, Resume
from app.schemas.candidate import (
    CandidateCreate,
    CandidateOut,
    DomainOut,
    HotspotOut,
    OpportunityOut,
    SkillOut,
    SnapshotOut,
)
from app.services.extraction import Extractor
from app.services.ingestion import IngestionError, ingest_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])

# Server-generated upload keys are UUIDs; anything else is rejected before it
# can touch the filesystem (path traversal guard).
_FILE_KEY_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _candidate_out(candidate: Candidate) -> CandidateOut:
    return CandidateOut(
        id=candidate.id,
        status=candidate.status,
        name=candidate.name,
        current_title=candidate.current_title,
        years_exp=candidate.years_exp,
        seniority=candidate.seniority,
        signal_score=candidate.signal_score,
        created_at=candidate.created_at,
    )


async def _get_candidate_or_404(session: AsyncSession, candidate_id: str) -> Candidate:
    candidate = await session.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="candidate not found"
        )
    return candidate


@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    body: CandidateCreate,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    extractor: Extractor = Depends(get_extractor),
) -> CandidateOut:
    if not _FILE_KEY_RE.match(body.file_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="invalid file_key"
        )
    if body.mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"unsupported content type: {body.mime_type}",
        )

    path = settings.storage_dir / body.file_key
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="uploaded file not found"
        )
    content = path.read_bytes()

    resume = Resume(
        file_key=body.file_key,
        filename=body.filename,
        mime_type=body.mime_type,
        size_bytes=len(content),
    )
    session.add(resume)
    await session.flush()

    try:
        candidate = await ingest_resume(session, resume, content, extractor)
    except IngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    return _candidate_out(candidate)


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: str, session: AsyncSession = Depends(get_session)
) -> CandidateOut:
    candidate = await _get_candidate_or_404(session, candidate_id)
    return _candidate_out(candidate)


@router.get("/{candidate_id}/snapshot", response_model=SnapshotOut)
async def get_snapshot(
    candidate_id: str, session: AsyncSession = Depends(get_session)
) -> SnapshotOut:
    candidate = await _get_candidate_or_404(session, candidate_id)

    matches = sorted(candidate.matches, key=lambda m: m.score, reverse=True)

    # Aggregate matched jobs into per-city hotspots (nightly demand_aggregates
    # job replaces this in v0.5).
    cities: dict[tuple[str, str | None], dict] = {}
    for match in matches:
        job = match.job
        if not job.city:
            continue
        cell = cities.setdefault(
            (job.city, job.country_code),
            {"lat": job.lat, "lon": job.lon, "open_roles": 0},
        )
        cell["open_roles"] += 1

    hotspots = [
        HotspotOut(
            city=city,
            country_code=cc,
            lat=cell["lat"],
            lon=cell["lon"],
            open_roles=cell["open_roles"],
            demand_score=min(100, round(100 * math.log(cell["open_roles"] + 1) / math.log(1000))),
        )
        for (city, cc), cell in cities.items()
    ]
    hotspots.sort(key=lambda h: h.open_roles, reverse=True)

    opportunities = [
        OpportunityOut(
            job_id=m.job.id,
            title=m.job.title,
            company=m.job.company,
            city=m.job.city,
            country_code=m.job.country_code,
            seniority=m.job.seniority,
            comp_min=m.job.comp_min,
            comp_max=m.job.comp_max,
            currency=m.job.currency,
            match_pct=round(m.score * 100),
        )
        for m in matches[:6]
    ]

    return SnapshotOut(
        candidate=_candidate_out(candidate),
        skills=[SkillOut(name=s.skill, weight=s.weight) for s in candidate.skills],
        domains=[DomainOut(name=d.domain, weight=d.weight) for d in candidate.domains],
        hotspots=hotspots[:30],
        opportunities=opportunities,
        markets_matched=len(hotspots),
    )


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: str,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    """Hard delete: candidate, skills/domains/matches, resume row, and the file (GDPR)."""
    candidate = await _get_candidate_or_404(session, candidate_id)

    resume = await session.get(Resume, candidate.resume_id)
    if resume is not None:
        stored = settings.storage_dir / resume.file_key
        stored.unlink(missing_ok=True)
        await session.delete(resume)

    await session.delete(candidate)
    await session.commit()
    logger.info("candidate deleted", extra={"ctx": {"candidate_id": candidate_id}})
