"""The synchronous v0.1 pipeline: parse → extract → embed → match → score.

Runs inside the POST /candidates request (no queue yet, per the roadmap).
Domain failures (unparseable file, LLM outage) mark the resume/candidate rows
failed and raise IngestionError — they must never surface as a 500.
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candidate, CandidateDomain, CandidateSkill, Job, Match, Resume
from app.services.embedding import candidate_embedding_text, embed_text
from app.services.extraction import ExtractionError, Extractor
from app.services.matching import rank_jobs
from app.services.parsing import ParsingError, parse_resume
from app.services.scoring import signal_score

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Domain failure the API maps to a 422, never a 500."""


async def ingest_resume(
    session: AsyncSession,
    resume: Resume,
    content: bytes,
    extractor: Extractor,
) -> Candidate:
    candidate = Candidate(resume_id=resume.id, status="parsing")
    session.add(candidate)
    resume.status = "parsing"
    await session.flush()

    try:
        text = parse_resume(content, resume.mime_type)
        extraction = extractor.extract(text)
    except (ParsingError, ExtractionError) as exc:
        resume.status = "failed"
        resume.error = str(exc)
        candidate.status = "failed"
        candidate.error = str(exc)
        await session.commit()
        logger.warning(
            "ingestion failed",
            extra={"ctx": {"resume_id": resume.id, "error": str(exc)}},
        )
        raise IngestionError(str(exc)) from exc

    resume.status = "parsed"
    candidate.name = extraction.name
    candidate.current_title = extraction.current_title
    candidate.years_exp = extraction.years_experience
    candidate.seniority = extraction.seniority
    candidate.embedding = embed_text(candidate_embedding_text(extraction))

    for skill in extraction.skills:
        session.add(
            CandidateSkill(candidate_id=candidate.id, skill=skill.name, weight=skill.weight)
        )
    for domain in extraction.domains:
        session.add(
            CandidateDomain(candidate_id=candidate.id, domain=domain.name, weight=domain.weight)
        )

    jobs = (await session.execute(select(Job))).scalars().all()
    ranked = rank_jobs(candidate.embedding, candidate.seniority, jobs)
    for job, score in ranked:
        session.add(Match(candidate_id=candidate.id, job_id=job.id, score=score))

    top_score = ranked[0][1] if ranked else 0.0
    # v0.1 simplification: a role marked current gets the full recency bonus.
    has_current_role = any(r.end in (None, "present") for r in extraction.roles)
    months_since_last_role = 0 if has_current_role else 12
    candidate.signal_score = signal_score(
        top_match_score=top_score,
        open_roles=len(ranked),
        months_since_last_role=months_since_last_role,
        domain_weights=[d.weight for d in extraction.domains],
    )
    candidate.status = "matched"
    await session.commit()

    logger.info(
        "candidate ingested",
        extra={
            "ctx": {
                "candidate_id": candidate.id,
                "signal_score": candidate.signal_score,
                "matches": len(ranked),
            }
        },
    )
    return candidate
