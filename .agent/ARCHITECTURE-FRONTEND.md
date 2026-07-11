# Isobar — Frontend & Product Architecture

> Module 1 of 2, split from `ISOBAR-ARCHITECTURE.md`. Covers the product overview, UX/design system, and the Next.js frontend. Backend, data model, pipeline, infrastructure, and security live in [ARCHITECTURE-BACKEND.md](./ARCHITECTURE-BACKEND.md).

> **Isobar** is a talent-intelligence app. Upload a résumé, get back (1) a live world heatmap of where matching roles are hiring right now and (2) a clean breakdown of the candidate's expertise as a skill mix. Enterprise dashboard on top; boring, pragmatic plumbing underneath.

---

## Contents

1. [Overview](#1-overview)
2. [User experience & design](#2-user-experience--design)
3. [Frontend](#3-frontend)
4. [Appendix — mockup reference](#appendix--mockup-reference)

---

## 1. Overview

Isobar answers two questions for a candidate or a recruiter, using nothing but a résumé:

- **Where in the world is this profile actually in demand right now?**
- **What is this candidate actually good at, expressed as a weighted skill mix?**

### Core capabilities

| Capability | Description |
|---|---|
| Résumé ingestion | Accept PDF/DOCX, parse it into structured data (skills, roles, years, seniority). |
| Signal scoring | Assign an overall "signal score" (0–100) based on skill match, market depth, and recency. |
| Global demand heatmap | Show hiring hotspots geographically, weighted by open-role count and match strength. |
| Expertise breakdown | Weighted donut of the candidate's domains (cloud, ML, backend, data, DevOps, product…). |
| Ranked opportunities | Table of live openings across matched regions, with comp bands and fit %. |

### Non-goals for v1

- Not a jobs board — Isobar shows where roles exist, not full application flows.
- Not an ATS — it doesn't manage a hiring pipeline.
- Not a résumé builder or writer.

---

## 2. User experience & design

The UX is a single-page enterprise dashboard. The reference mockup lives at `isobar-talent-signal-dashboard.html` (the HTML file rendering the design shown below).

![Isobar dashboard mockup](../isobar-mockup.png)

### Layout

The screen is split into a **76 px navigation rail** on the left and a **~1200 px main area** on the right. The main area stacks vertically:

1. **Top bar** — brand mark, breadcrumb ("Resume analysis / live session"), search, `Export report`, `Upload résumé`.
2. **Summary strip** — candidate avatar, name, current title/years, filename, top skill tags, **Signal score** (0–100), **Markets matched** count.
3. **Two-column grid**:
   - **Left (~63%)**: Global demand heatmap — dot-matrix world cartogram with pulsing signal markers at hiring hotspots. Hover any marker for city, coordinates, demand score, and open-role count.
   - **Right (~37%)**: Expertise donut, top regions list with progress bars, skill signal cloud.
4. **Matching opportunities table** — ranked list of live openings with region, role focus, seniority pill, comp band, openings count, and match %.

### Design system

The mockup fixes concrete tokens so implementation stays consistent:

| Token | Value | Usage |
|---|---|---|
| `--ink` | `#090D18` | App background |
| `--panel` | `#10182B` | Card surfaces |
| `--panel-2` | `#161F38` | Nested surfaces, chip backgrounds |
| `--border-soft` | `#1A2338` | Card borders |
| `--text-1` | `#EAEEF9` | Primary text |
| `--text-2` | `#8D97B3` | Secondary text |
| `--amber` | `#F5A623` | Primary accent, high-demand hotspots, key metrics |
| `--cyan` | `#3ED6C4` | Low-demand hotspots, secondary highlights |
| `--crimson` | `#FF5470` | Top-tier hotspots, alerts |
| `--violet` | `#7C8CF8` | Expertise segment |
| `--sage` | `#8FD19E` | Expertise segment |

**Type**:
- **Space Grotesk** for display headers and candidate name.
- **Inter** for UI and body.
- **IBM Plex Mono** for numbers, coordinates, comp figures, scores.

Radius `14 px` on cards, `8 px` on chips, `999px` for pills. Subtle 28 px dot-grid background on `--ink`.

### Interaction notes

- Map markers pulse (2.4 s ease-out) to communicate live data; motion is disabled under `prefers-reduced-motion: reduce`.
- Tooltip on hover only, positioned to avoid the right edge; auto-hides on `mouseleave`.
- Toggle above the map switches between "This role" and "All matches" scope.

---

## 3. Frontend

**Stack** — deliberately small.

| Concern | Choice |
|---|---|
| Framework | **Next.js 15** (App Router), TypeScript |
| Styling | **Tailwind CSS** + a small CSS-var theme file that ports the mockup tokens |
| Component primitives | **shadcn/ui** (button, dialog, dropdown, table) |
| Charts | **Recharts** (donut, progress bars) |
| Map | **react-simple-maps** + world-atlas TopoJSON (110 m resolution) |
| Data fetching | **TanStack Query** |
| Auth | **Clerk** (dev + team plans support SSO/SAML) |
| Icons | **lucide-react** |

The mockup is production-realistic: it uses vanilla HTML+CSS+SVG so the port to React is 1-to-1 — replace `<script>`-generated dots with `react-simple-maps` `<Geographies>`, replace inline SVG donut with a `<PieChart>` from Recharts, wrap sections in components.

### App structure

```
app/
├── (marketing)/
│   └── page.tsx                    # landing
├── (app)/
│   ├── layout.tsx                  # nav rail + top bar
│   ├── dashboard/
│   │   └── page.tsx                # server component — fetches candidate snapshot
│   ├── upload/
│   │   └── page.tsx                # drag-drop uploader
│   └── candidates/[id]/
│       ├── page.tsx                # the dashboard shown in the mockup
│       └── loading.tsx
├── api/                            # thin BFF routes for uploads
└── lib/
    ├── api-client.ts               # typed fetch wrapper
    ├── query-keys.ts
    └── theme.ts                    # design tokens as JS

components/
├── layout/
│   ├── nav-rail.tsx
│   └── top-bar.tsx
├── candidate/
│   ├── summary-strip.tsx           # avatar + name + tags + signal score
│   ├── demand-heatmap.tsx          # react-simple-maps + markers + tooltip
│   ├── expertise-donut.tsx         # recharts
│   ├── top-regions.tsx
│   ├── skill-cloud.tsx
│   └── opportunities-table.tsx
└── ui/                             # shadcn primitives
```

### Key components (contracts, kept short)

```ts
// demand-heatmap.tsx
type Hotspot = {
  city: string; country: string;
  lat: number; lon: number;
  demandScore: number;     // 0–100
  openRoles: number;
  tier: 'cool' | 'warm' | 'hot';
};
<DemandHeatmap hotspots={hotspots} scope="thisRole" />

// expertise-donut.tsx
type Domain = { name: string; weight: number; color: string };
<ExpertiseDonut domains={domains} centerLabel="6 domains" />

// opportunities-table.tsx
<OpportunitiesTable candidateId={id} pageSize={6} />
```

### Data flow

1. User uploads → BFF route in `app/api/upload` requests a presigned S3 URL from the backend, uploads directly to S3, then `POST /candidates` to trigger parsing.
2. UI transitions to `/candidates/[id]` and opens a Server-Sent Events stream for parsing progress (`file → parsed → analyzed → matched`).
3. Once `matched`, the dashboard fetches the snapshot in one call: `GET /candidates/:id/snapshot` returns candidate summary, expertise mix, hotspots aggregate, and page 1 of opportunities.
4. Table paginates independently via TanStack Query.

The API surface these calls hit is defined in [ARCHITECTURE-BACKEND.md](./ARCHITECTURE-BACKEND.md#3-backend).

---

## Appendix — mockup reference

The definitive UI reference is `isobar-talent-signal-dashboard.html`. Open it in any browser to interact with the map, tooltips, and the donut. Every component listed in Section 3 has its visual counterpart in that file.
