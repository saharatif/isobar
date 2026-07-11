# PROGRESS — Isobar Backend

Tracking against the v0.1 "internal demo" milestone in
[.agent/ARCHITECTURE-BACKEND.md](.agent/ARCHITECTURE-BACKEND.md) §8.

_Last updated: 2026-07-11_

## Status: v0.1 backend complete ✅ (81/81 tests passing — see `all_tests.txt`)

## Done

- [x] **Project setup** — uv-managed deps in `pyproject.toml`; pytest configured (`backend/tests`).
- [x] **Config** — `pydantic-settings` with `.env` support; API key as `SecretStr`; `.env.example` added; `.env` gitignored.
- [x] **Structured JSON logging** — `logging_config.py`; no PII/secrets in logs.
- [x] **Data model** — `resumes`, `candidates`, `candidate_skills`, `candidate_domains`, `jobs`, `matches` (SQLAlchemy 2.x async; SQLite for demo, same shape as the target Postgres schema).
- [x] **Stage 1 — Parse** — PDF (PyMuPDF), DOCX (python-docx), text/markdown; scanned-PDF detection (<100 chars/page) rejects with a clear error (OCR is v0.5).
- [x] **Stage 2 — Extract** — Claude structured outputs (`messages.parse` + Pydantic `Extraction` schema, model `claude-opus-4-8`, prompt-injection-hardened) with an offline `KeywordExtractor` fallback for demo mode / tests.
- [x] **Embedding** — deterministic hashing embedder (v0.1 stand-in for bge-large-en-v1.5), L2-normalized, 128-dim.
- [x] **Stage 3 — Match** — cosine ranking + seniority ±1 tier filter over the seeded jobs table; results persisted to `matches`.
- [x] **Signal score** — the exact §5 formula (0.55 match + 0.25 market depth + 0.10 recency + 0.10 breadth), bounded 0–100, every component unit-tested.
- [x] **API** — `GET /health`, `POST /uploads` (multipart, type/size/empty validation), `POST /candidates` (runs the sync pipeline), `GET /candidates/:id`, `GET /candidates/:id/snapshot` (summary + skills + domains + hotspots + opportunities), `DELETE /candidates/:id` (GDPR hard delete incl. stored file).
- [x] **Demo seed** — 10 jobs across 9 cities so the heatmap/opportunities render (roadmap's "hard-coded city list").
- [x] **Tests** — 81 tests across scoring, matching, parsing, extraction, embedding, and end-to-end API (incl. path traversal, oversized/empty/unsupported uploads, unparseable-file-is-422-not-500). Full log: `all_tests.txt`.
- [x] **Live smoke test** — booted uvicorn, ran upload → candidate → snapshot end to end (demo mode): signal score 76, 8 markets matched, ranked opportunities.

## Architecture deltas (v0.1 stand-ins, intentional)

| Target (architecture doc) | v0.1 implementation |
|---|---|
| Postgres + pgvector | SQLite (async SQLAlchemy), embeddings as JSON, cosine in Python |
| S3/R2 presigned uploads | Direct multipart upload to local disk |
| Redis + Arq worker, SSE progress | Synchronous parse inside `POST /candidates` |
| Mistral OCR for scanned PDFs | Rejected with a clear 422 |
| bge-large-en-v1.5 embeddings | Deterministic hashing embedder |
| Adzuna nightly ingest | Hard-coded demo job seed |
| Clerk auth + org RLS | No auth (single-tenant demo) |
| Claude Sonnet 4.6 | `claude-opus-4-8` (current recommended model; configurable via `ANTHROPIC_MODEL`) |

## Blocked

- **Live Claude extraction** — Anthropic account has insufficient credits (see BUGS.md C1). Demo currently runs on the offline keyword extractor.

## Next (v0.5 candidates)

- [ ] Clerk JWT auth + org tenancy
- [ ] Redis + Arq async pipeline with SSE progress events
- [ ] Postgres + pgvector migration (Alembic)
- [ ] Real embeddings (bge-large-en-v1.5)
- [ ] Adzuna job ingest cron + nightly `demand_aggregates`
- [ ] Mistral OCR path for scanned PDFs
- [ ] Cost/rate-limit guardrails on LLM calls

## How to run

```bash
uv run uvicorn app.main:app --app-dir backend --reload   # API on :8000
uv run pytest -v                                          # test suite
```

Set `ANTHROPIC_API_KEY` in `.env` for real Claude extraction; leave it unset
for offline demo mode.
