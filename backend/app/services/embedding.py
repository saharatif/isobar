"""Deterministic hashing embedder — v0.1 stand-in for bge-large-en-v1.5.

Feature-hashes tokens into a fixed-size L2-normalized vector. Not semantically
smart, but deterministic, dependency-free, and good enough to exercise the
cosine-matching path end to end. Swap for sentence-transformers in v0.5.
"""
import hashlib
import math
import re

from app.schemas.extraction import Extraction

EMBEDDING_DIM = 128

_TOKEN_RE = re.compile(r"[a-z0-9+#.]+")


def embed_text(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    vec = [0.0] * dim
    for token in _TOKEN_RE.findall(text.lower()):
        digest = int(hashlib.md5(token.encode()).hexdigest(), 16)
        index = digest % dim
        sign = 1.0 if (digest >> 16) % 2 == 0 else -1.0
        vec[index] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def candidate_embedding_text(extraction: Extraction) -> str:
    """Concatenate roles + skills + domains, mirroring the target pipeline."""
    parts: list[str] = []
    for role in extraction.roles:
        parts.extend(p for p in (role.title, role.company) if p)
    parts.extend(s.name for s in extraction.skills)
    parts.extend(d.name for d in extraction.domains)
    if extraction.current_title:
        parts.append(extraction.current_title)
    return " ".join(parts)
