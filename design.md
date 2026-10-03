# HCMS UI — Design Specification

Figma-faithful rebuild of the recruitment flow, shipped in commit `fb3ba14`
(2026-05-26) as a standalone `ui` Django app. Pure UI only — no backend wiring.

Source design: [HCMS on Figma](https://www.figma.com/design/HifgiWqVPte5z0Vu1KXCzW/HCMS)

---

## App Structure

| Path | Purpose |
|------|---------|
| [ui/](ui/) | Django app — views/urls only, no models |
| [ui/urls.py](ui/urls.py) | 11 page routes under `/ui/<page>/` |
| [ui/views.py](ui/views.py) | Thin `render()` views, one per page |
| [templates/ui/](templates/ui/) | All 11 page templates + shared `base.html` |
| [figma-pages.md](figma-pages.md) | Page index with Figma node-ids, screenshots, notes |

Mounted in [fits/urls.py](fits/urls.py) at `/ui/`. `ui` is registered in
`INSTALLED_APPS` ([fits/settings.py](fits/settings.py)).

---

## Color System

Tokens are inlined in [templates/ui/base.html](templates/ui/base.html) (no CSS
variables yet — values are hard-coded per template).

| Token | Hex | Usage |
|-------|-----|-------|
| Primary Accent | `#1F5F2F` | Dark green — logo, active sidebar, primary buttons |
| Light Accent | `#4DC55C` | Medium green — hover, accents |
| Active BG | `#E8F0EA` | Active sidebar item background |
| Hover BG | `#F4F6F4` | Sidebar hover |
| Page BG | `#F5F6FA` | Body background |
| Card BG | `#FFFFFF` | Cards, sidebar, navbar |
| Border | `#E8E8E8` / `#EFEFEF` | Dividers, card borders |
| Heading | `#111` / `#222` | Titles, body |
| Body Text | `#555` | Default text |
| Muted | `#777` / `#999` / `#ABABAB` | Subtitles, labels, section headers |
| Warning | `#C04730` | Destructive actions |
| Link | `#4A70EA` | Inline links |
| Alert | `#DC3519` | Errors |

---

## Typography

- Family: **Inter** (Google Fonts, weights 400/500/600/700)
- Icon set: **Material Symbols Outlined** (Google Fonts)
- Base font-size: **13px** on `<body>`; sidebar items 12px; section labels 9px
  uppercase tracked `0.08em`

---

## Layout

```
┌─────────────┬───────────────────────────────────┐
│             │  Navbar  56px  sticky             │
│  Sidebar    ├───────────────────────────────────┤
│  220px      │                                   │
│  fixed      │  Main content                     │
│             │  (per-page)                       │
└─────────────┴───────────────────────────────────┘
```

- Sidebar: 220px fixed, white, scroll-y, full-height
- Navbar: 56px sticky top
- Main: `margin-left: 220px`, flex column

---

## Pages

All 11 pages extend [base.html](templates/ui/base.html) and live at `/ui/<slug>/`.

| # | Page | URL | Template | Figma Node |
|---|------|-----|----------|------------|
| 1 | Dashboard | `/ui/dashboard/` | [dashboard.html](templates/ui/dashboard.html) | 12-15 |
| 2 | Candidates | `/ui/candidates/` | [candidates.html](templates/ui/candidates.html) | 56-85 |
| 3 | Job Requisition | `/ui/job-requisition/` | [job_requisition.html](templates/ui/job_requisition.html) | 46-36 |
| 4 | JD Creator | `/ui/jd-creator/` | [jd_creator.html](templates/ui/jd_creator.html) | 46-947 |
| 5 | Approvals | `/ui/approvals/` | [approvals.html](templates/ui/approvals.html) | 46-336 |
| 6 | Manpower Request | `/ui/manpower-request/` | [manpower_request.html](templates/ui/manpower_request.html) | 65-148 |
| 7 | Manpower Approval | `/ui/manpower-approval/` | [manpower_approval.html](templates/ui/manpower_approval.html) | 79-506 |
| 8 | Interview | `/ui/interview/` | [interview.html](templates/ui/interview.html) | 56-416 |
| 9 | Interview Creator | `/ui/interview-creator/` | [interview_creator.html](templates/ui/interview_creator.html) | 60-906 |
| 10 | Offers | `/ui/offers/` | [offers.html](templates/ui/offers.html) | 61-1523 |
| 11 | Offer Creator | `/ui/offer-creator/` | [offer_creator.html](templates/ui/offer_creator.html) | 61-1309 |

---

## Component Classes (base.html)

Shared, BEM-style under `ui-` prefix:

- `.ui-wrapper`, `.ui-sidebar`, `.ui-main`, `.ui-navbar` — layout shell
- `.ui-sidebar__logo`, `.ui-sidebar__item`, `.ui-sidebar__section`,
  `.ui-sidebar__bottom` — sidebar
- Per-page styles live inline within each template (no shared component CSS
  beyond the shell)

---

## Status & Next Steps

- **Status**: Static UI complete for all 11 pages; backend integration not yet
  started. The existing recruitment flow under `/recruitment/...` is unchanged.
- **Wiring plan**: Replace the per-page `views.py` `render()` stubs with real
  context from `recruitment/` views, then point sidebar menu entries from the
  legacy templates to the `ui:` URL names once each page reaches parity.
- **Migration ordering**: Update [figma-pages.md](figma-pages.md) `Status`
  column (`todo → in-progress → done`) as each page is wired.

---

## Conventions

- Pure HTML/CSS, no JS framework — matches the rest of the project (HTMX +
  jQuery available but not required for these static pages).
- Inline `<style>` blocks per template are acceptable for now; consolidate into
  a shared stylesheet only after the design stabilises.
- All copy uses English literals; pages have not yet been wrapped in `{% trans %}`.
