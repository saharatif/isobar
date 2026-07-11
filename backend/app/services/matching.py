"""Stage 3 — Match: candidate embedding vs job embeddings.

v0.1 computes cosine similarity in Python over the whole (small, seeded) jobs
table; the pgvector HNSW two-step search replaces this at real data volume.
"""
import math
from typing import Protocol, Sequence

SENIORITY_ORDER = ["junior", "mid", "senior", "staff", "principal"]


class JobLike(Protocol):
    embedding: list | None
    seniority: str | None


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"vector length mismatch: {len(a)} != {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def seniority_compatible(candidate: str | None, job: str | None) -> bool:
    """Within ±1 tier. Unknown seniority on either side passes the filter."""
    if candidate is None or job is None:
        return True
    try:
        ci = SENIORITY_ORDER.index(candidate)
        ji = SENIORITY_ORDER.index(job)
    except ValueError:
        return True
    return abs(ci - ji) <= 1


def rank_jobs(
    candidate_embedding: Sequence[float],
    candidate_seniority: str | None,
    jobs: Sequence[JobLike],
    top_k: int = 50,
) -> list[tuple[JobLike, float]]:
    """Return (job, score 0..1) sorted best-first, seniority-filtered."""
    scored = []
    for job in jobs:
        if not job.embedding:
            continue
        if not seniority_compatible(candidate_seniority, job.seniority):
            continue
        score = max(0.0, cosine_similarity(candidate_embedding, job.embedding))
        scored.append((job, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]
