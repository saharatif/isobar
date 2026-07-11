# BUGS — Isobar Backend

Issues found during development and review, categorized by severity per the
Team Lead review process. Status: **open** / **fixed** / **accepted** (known
v0.1 limitation, tracked for a later milestone).

---

## Critical

_None open._

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| C1 | Anthropic API rejects all extraction calls with 400 — **account credit balance is too low**. Résumé ingestion via Claude fails until credits are added. | **open (environment, not code)** | Verified 2026-07-11 against the live API. The pipeline degrades correctly (422 to the client, resume marked `failed`, no crash, no key in logs). Workaround: unset `ANTHROPIC_API_KEY` to run in offline demo mode (keyword extractor). Fix: add credits at console.anthropic.com → Plans & Billing. |

## Major

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| M1 | No authentication on any endpoint — anyone who can reach the API can upload, read, and delete candidates. | **accepted (v0.1)** | Roadmap: Clerk JWT + org tenancy is v0.5 scope. Must not be deployed publicly before then. |
| M2 | Synchronous parse in the request thread — a slow LLM call blocks the worker for the whole request. | **accepted (v0.1)** | By design per roadmap v0.1 ("synchronous parse in the request"). Redis + Arq worker lands in v0.5. |
| M3 | Upstream Anthropic error detail was swallowed — logs showed only "LLM API error (400)", making billing vs. bad-request undiagnosable. | **fixed** | `ClaudeExtractor` now logs status + upstream message server-side; client response stays generic. |
| M4 | Failed `Resume`/`Candidate` rows accumulate with no cleanup or retry path. | **open (minor for demo)** | Add a retention sweep or retry endpoint when async pipeline lands. |

## Minor

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| m1 | Deprecated Starlette status constants (`HTTP_422_UNPROCESSABLE_ENTITY`, `HTTP_413_REQUEST_ENTITY_TOO_LARGE`) raised deprecation warnings. | **fixed** | Replaced with `HTTP_422_UNPROCESSABLE_CONTENT` / `HTTP_413_CONTENT_TOO_LARGE`. |
| m2 | Hashing embedder is not semantic — match percentages are only meaningful relative to each other, not as absolute quality. | **accepted (v0.1)** | Documented in `embedding.py`; bge-large-en-v1.5 replaces it in v0.5. |
| m3 | `months_since_last_role` is a crude heuristic (0 if any role is "present", else 12). | **accepted (v0.1)** | Real date math needs reliable role dates from the LLM extractor. |
| m4 | Upload content type trusted from the client's multipart header; no magic-byte sniffing. | **open** | Low risk (parser rejects mismatched content anyway) but worth adding `python-magic` later. |

---

## Security review notes (no open findings)

- `.env` is gitignored; `.env.example` has placeholders only. Verified no key
  material committed.
- API key held as `SecretStr`; never appears in logs or responses (verified in
  the C1 failure logs).
- Upload file keys are server-generated UUIDs and validated with a strict
  regex on `POST /candidates` — client input cannot form a filesystem path
  (path-traversal test: `test_malformed_file_key_rejected`).
- Prompt injection: résumé text is delimited in the user turn, instructions
  live in the system prompt only, and structured outputs constrain the
  response shape. Résumés are still untrusted input; revisit when extraction
  output starts driving actions beyond scoring.
- Résumés are PII: raw text is never logged; GDPR hard-delete removes DB rows
  and the stored file (`test_delete_removes_candidate_and_file`).
