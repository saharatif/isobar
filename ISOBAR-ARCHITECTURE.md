# Isobar — Architecture

> **Isobar** is a talent-intelligence app. Upload a résumé, get back (1) a live world heatmap of where matching roles are hiring right now and (2) a clean breakdown of the candidate's expertise as a skill mix. Enterprise dashboard on top; boring, pragmatic plumbing underneath.

---

The architecture is maintained as two modules under [`.agent/`](.agent/) to keep
the frontend and backend concerns separate. This file is a pointer only — the
modules below are the source of truth.

- **[.agent/ARCHITECTURE-FRONTEND.md](.agent/ARCHITECTURE-FRONTEND.md)** — product overview & non-goals, UX/design system, and the Next.js frontend (stack, app structure, component contracts, data flow). The frontend lives in [`Frontend/`](Frontend/).
- **[.agent/ARCHITECTURE-BACKEND.md](.agent/ARCHITECTURE-BACKEND.md)** — system architecture, FastAPI backend & API surface, data model, ingestion pipeline, matching/heatmap, infrastructure, security, and roadmap. The backend lives in [`backend/`](backend/).

## Implementation status

The v0.1 backend is implemented under [`backend/`](backend/); see
[PROGRESS.md](PROGRESS.md) for what's done vs. deferred and [BUGS.md](BUGS.md)
for known issues. Résumé extraction runs on the **OpenAI (ChatGPT) API**
(`gpt-4o` by default) with an offline keyword-extractor fallback for demo mode.

> Note: the original architecture doc specified Claude/Anthropic for extraction;
> the implementation was switched to OpenAI. The prose in the `.agent/` modules
> still references the original provider in places — treat the code and this
> note as authoritative where they differ.
