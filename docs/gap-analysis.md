# Gap analysis â€” old imlem.org vs. the current Flask app

> **Status update (rebuild complete).** Items 1â€“12, 14â€“19 and 20â€“30 below are addressed by the server-rendered rebuild (see README and `docs/pending-league-decisions.md` for what remains open). Corrections to this audit made after the import: (a) the old results name only *some* students (e.g. 39 of 1,226 rows in 2015-16, 107 of 967 in 2025-26), not about 1,000 a year as first estimated; (b) the archive holds 12,337 individual rows across 11 seasons (about 11,000 was my first estimate), and 2019-20 has only four meets; (c) the Coaches' Corner is still a placeholder and the old admin/coach dashboards were removed at the league's request.

Baseline: the current `imlem-redesign` app (audited from `app.py`, `static/app.js`, `templates/index.html`, `data/*.json`, README, DEPLOYMENT) against [site-inventory.md](site-inventory.md).

## What the current app is

A hash-routed single-page app (`#/â€¦`, one `index.html`, 1,200 lines of JS building the DOM) over a JSON API with file-backed storage. It has admin and coach logins, five sections (Meet Information, Standings, Statistics, Study Materials, Coaches' Corner, Links), and a data model of **divisions â†’ teams (schools) with five integer scores**. It contains essentially **no real IMLEM content**: `meets.json`, `statistics.json` are empty, `divisions.json` has 12 empty divisions plus a fake "Sample Elementary", and `study-materials.json` has one PDF.

## Gaps (old site has it; new app is missing, broken, or worse)

Severity: **P0** loses archive content / parity, **P1** major feature, **P2** polish.

### Content and archive â€” everything is missing (P0)

| # | Old site | Current app |
|---|---|---|
| 1 | Individual rankings, 11 seasons (2015-16 â†’ 2025-26), ~11,000 rows Ã— 40 columns, with ranks by overall/division/grade and per-round scores | No individual results at all. The data model is "5 integers per team." |
| 2 | Team rankings by division, 11 seasons, 11â€“12 divisions each | Only one season's flat scores; no year dimension |
| 3 | Overall team rankings with cluster column, 11 seasons | None |
| 4 | Round topics, 12 seasons (2015-16 â†’ 2026-27), including the **2026-27** season now in progress | None |
| 5 | Dates and sites by cluster, 10 seasons | None; meets are a flat list with one date/location |
| 6 | Cluster pages (member schools, sites, coordinator) for 7 seasons, incl. Pennsylvania cluster | None; no concept of clusters |
| 7 | League officers and coordinators, 2015-16 â†’ 2022-23 | None |
| 8 | League Bylaws (2003), the rules document | Missing. (Calculator rules are already present, and their text matches the old page.) |
| 9 | Contact pages + "Who should I contact?" routing table | Hard-coded placeholder; real names/addresses/routing absent |
| 10 | Links page (5 sections, ~35 sites) | Has a single link (AoPS Massachusetts forum); the other ~35 are missing |
| 11 | Study materials: external archive of ~54 contest PDFs on matharchive.org, question bank, quiz generator, Ellison books, 5 video playlists, Lexington archive | Upload-only list; none of these links or files present |
| 12 | 2015-16 topics PDF | Not migrated |
| 13 | 50th-anniversary GIF/branding | Covered: `50-years.png` is used as the home-page hero image |

### URLs and SEO (P0)

| # | Gap |
|---|---|
| 14 | **No old URL redirects.** All ~250 old paths (`/statistics/202526/202526_team.html`, `/meetinfo/...`, `/leagueinfo/...`, etc.) would 404 â€” every bookmark and Google result breaks. |
| 15 | SPA with hash routes: individual results/pages have no real URLs, so they can't be indexed, shared, or printed; nothing works without JavaScript. |
| 16 | No `sitemap.xml`, `robots.txt`, per-page titles/descriptions/Open Graph (one static `<title>` for the whole app). |

### Features that exist in the old site and are done worse (P1)

| # | Old site | Current app |
|---|---|---|
| 17 | Sortable stats tables (sorttable.js), anchors per division | Tables exist for current scores only; no search, filter, year selector, mobile layout |
| 18 | Breadcrumbs on every page | None |
| 19 | Printable, plain, fast static pages | Entire UI rendered by one 48 KB script; no print styles |

### Features the new app has that the old site lacks (keep / improve)

- Admin and coach logins, coach rosters, score entry, PDF upload, meet announcements. **Note:** the old site had none of this; nothing there says IMLEM staff want it. Please confirm which of these you actually want (see questions) before I invest in polishing them.

### Quality, security, and ops issues found in the current app (P0/P1)

| # | Finding | Severity |
|---|---|---|
| 20 | **No CSRF protection** on state-changing JSON endpoints (cookie auth, `SameSite=Lax` only) | P0 |
| 21 | **Default credentials seeded** (`admin@imlem.org`/`admin123`, `coach@imlem.org`/`coach123`) written into `users.json` whenever the file is missing, and documented in DEPLOYMENT.md. Password hashes are committed in `data/users.json` | P0 |
| 22 | `.gitignore` excludes `data/` and `uploads/`, so **the data and uploaded PDFs are not in version control** â€” contradicts "never lose archive content" | P0 |
| 23 | Upload validation trusts the client `Content-Type` header; no magic-byte check, no filename/path validation of `year`, `meetNumber`, `type` (path components come straight from form fields â†’ path traversal risk), 50 MB limit for PDFs | P0 |
| 24 | `/api/divisions/.../teams/...` score update accepts any JSON type as `score` (not validated); roster update stores unvalidated arbitrary JSON; `PUT /api/my-school` has no size/type limits | P1 |
| 25 | No login rate limiting / brute-force protection | P1 |
| 26 | File-based JSON read-modify-write with no locking â†’ concurrent writes can lose data | P1 |
| 27 | `datetime.utcnow()` deprecated; `app.run(host='0.0.0.0')` default | P2 |
| 28 | No tests; no `pytest` in requirements | P1 |
| 29 | README/DEPLOYMENT describe the SPA; will need rewriting. DEPLOYMENT says "no self-service password-change UI yet," but one exists | P2 |
| 30 | Not a git repository (no history, no branch to work on) | P1 |

### Accessibility / design (P1)

The SPA renders everything client-side; no verified WCAG 2.1 AA conformance (focus management on route change, landmarks, table semantics), no print styles, no 404 page, no mobile-first table layout. Existing styles/assets (logo, icons, Pexels stock banners) are reusable, but the stock student photos are not IMLEM photos â€” decide whether to keep them.

## Proposed architecture to close the gaps

1. **Server-rendered Flask (Jinja2) with real URLs** instead of the hash SPA, progressive JS enhancement only for sorting/filtering. Keeps Flask + JSON/SQLite simple for hosting.
2. **Results in SQLite** (read-only for the public; imported once from the mirror by a script that never touches the originals) instead of giant JSON, so search by year/division/school/student is fast. The original HTML stays untouched in an `archive/` folder as the source of truth and is also served as static "legacy view" pages if a parse ever looks wrong.
3. **Redirect map** (`/statistics/202526/202526_team.html` â†’ `/results/2025-26/teams`, and so on) for every old URL; test asserts every crawled URL resolves to 200 or 301â†’200.
4. Keep existing auth, but add CSRF, remove seeded default accounts (first-run admin from env/CLI), validate uploads, and move `data/` and `uploads/` out of `.gitignore` for the archive portions.
5. New pages: home with next meet/countdown/announcements, 50th anniversary, 404, sitemap, robots, OG tags.

## Open questions (I won't guess on these)

1. **Coaches' Corner is behind HTTP auth and I can't see it.** Can you export its pages/files (or give me read access)? Until then it's a gap I can't close.
2. **Student names:** the old results publish "first name + last initial", grade and school for ~1,000 students/year. Do you want these carried over as-is, searchable by student name, or hidden/limited for recent years? (Minors' data; I'd default to *as-is on the page, but not indexable by search engines for individual pages* if you agree.)
3. **Contest PDFs/solutions live on matharchive.org.** Do you own/control that host? May I download and mirror those ~54 PDFs into `uploads/`, or should the site keep linking out (with a note that the archive is external)?
4. **Registration/sign-up:** the old site has none (joining = email the President). Do you want an online "join the league / register a team" form (what fields, where should submissions go â€” email, admin inbox, spreadsheet?), or just clear instructions?
5. **Contact details:** the old site publishes obfuscated emails (`kelly_LASTNAME@â€¦`). Should I keep that pattern, build a contact form that emails the right officer, or something else? Who are the current officers for 2025-26/2026-27 (the old site's list stops at 2022-23)?
6. **Admin/coach login dashboards** (existing) â€” keep, simplify, or drop? Who would use them?
7. **"IMLEM Meet Information -- 2024-25.html"**: I could not find this file on disk; I believe it's the old site's `/meetinfo/202425/202425datessites.html` (same title), which I have from the crawl. If it's a separate file, please drop it into the repo.
8. **Scoring rules / divisions:** is the division list for 2026-27 the same as 2025-26 (the old site comments out some)? I'd derive each season's divisions from that season's own results.
9. **Deployment target** (host, domain, HTTPS) â€” the old HTTPS is broken, so I need to know where this will live.
