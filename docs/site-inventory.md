# Old site inventory — imlem.org

Audited 2026-10-12 by crawling `http://imlem.org/` and following every internal link (253 pages/files fetched, 7 errors, 146 distinct external/mailto targets). The raw mirror was saved outside the repo during the audit and is the source for migration.

## Technical notes about the old site

- **HTTPS is broken.** `https://imlem.org` fails the TLS handshake in modern clients (no common protocol/cipher; reproduced with both curl/schannel and the WebFetch tool). Only plain `http://` works. Every page loads its CSS/JS from `http://www.imlem.org/…`. The new site must serve HTTPS.
- **Static HTML only.** Apache, hand-written pages, no database, no CMS. **There are no forms anywhere** — no registration, sign-up, login, search, or upload on the public site.
- The only script is `sorttable.js` (click-to-sort column headers on statistics tables). CSS is `imlem.css` (single file).
- `favicon.ico`, `logos/50th_anniversary.gif` (homepage), and a `pdf.gif` icon are the only images.
- Pages use `…/index.html` style paths, and pages link to each other with relative paths. Breadcrumbs exist on every sub-page.
- `/coaches/index.html` returns **HTTP 401 (password-protected)**. Its contents could not be audited.
- Several links are dead on the old site (see "Broken links on the old site").

## Homepage (`/`)

Title: "Intermediate Math League of Eastern Massachusetts". An intro line, then seven collapsible `<details>` groups, the 50th-anniversary GIF at the side, and a footer link to Art of Problem Solving's Massachusetts forum.

| Group | Items |
|---|---|
| Meet Information | 2026-27 Round Topics (`/meetinfo/202627/202627topics.html`); Calculator policy (`/meetinfo/calculators.html`). Commented out: 2024-25 dates/sites, cluster links, directions to sites (`/directions/` — not on the server), "meet information from previous years" |
| Statistics | 2025-26 Individual Rankings; 2025-26 Team Rankings by Division (with anchor links to each division); 2025-26 Team Rankings Overall; "Statistics from previous years" |
| Study Materials | Past IMLEM meets (external: `matharchive.org/imlem/`); Study Materials index |
| League Information | 2024-25 Officers/Cluster Coordinators and Clusters (shown as "Pending", not linked); League Bylaws (2003) |
| Coaches' Corner | `/coaches/index.html` (password protected) |
| Contact Information | President, Tabulator, Treasurer, Contest Writer, "Who should I contact?" |
| Links | Five anchored sections on `/links/index.html` |

## Page inventory

### Meet Information (`/meetinfo/`)
- `/meetinfo/index.html` — hub listing every season from 2015-16 to 2024-25 (dates/sites, topics, cluster pages).
- `/meetinfo/calculators.html` — **Calculator rules**: allowed in meets 4 and 5, all team members should have one; programmable/graphing calculators not allowed.
- Per season folder `/meetinfo/YYYYYY/` (e.g. `202425`):
  - `…datessites.html` — table of 5 meet dates by cluster/host site, make-up dates in bold, "last cluster competes" row. Seasons: 2015-16 through 2024-25 (2025-26 and 2026-27 have no dates/sites page).
  - `…topics.html` — **Round topics** for Meets 1–5: Round 1 Mystery, 2 Geometry, 3 Number Theory, 4 Arithmetic, 5 Algebra, Team Round, with a per-meet date and "No Calculators"/"Calculator Meet" tag. Seasons 2015-16 through **2026-27** (2026-27 dates: Oct 15, Nov 19, Jan 14, Feb 25, Apr 1).
  - `201516/201516topics.pdf` — the only PDF on the site (printable topics for 2015-16).
  - `cluster/1.html … 15.html`, `pa.html` (Pennsylvania), `index.html` (ALL) — per-cluster member schools, meet dates/sites, coordinator contact. Present for 2015-16 → 2020-21 and 2024-25 only.
- Old-site bug: the 2024-25 dates page links its Meet headers to `201819topics.html` (404).

### Statistics (`/statistics/`)
- `/statistics/index.html` — hub for 11 seasons (2015-16 → 2025-26), three views each.
- Per season `/statistics/YYYYYY/`:
  - `…_individual.html` — **Individual rankings**, sortable. About 970 rows (2025-26) to 1,225 (2015-16), 40 columns: overall rank, division rank (e.g. `Pyt-1`), grade rank, name (first name + last initial), grade, school, division, then for each of 5 meets: rounds 1–5 scores + meet total, then 5-meet total and best-of total. Files are 440–760 KB each.
  - `…_team_bydivision.html` — **Team rankings by division**, one table per division, anchor `#euc #pyt #pas #fib #dav #mar #qua #mos #gau #hyp #ram` (+ `#und` "Undecided"). Per meet: score + rank; total.
  - `…_team.html` — **Overall team rankings**: rank, division rank, school, cluster, 5 × (score, rank), total.
- Division set changes by year (Lexington, Zubayda, Noether, Gardner, Liu Hui appear in comments/older years). Divisions used in 2025-26: Euclid, Pythagoras, Pascal, Fibonacci, da Vinci, Martinoli, Quaden, Mosca, Gauss, Hypatia, Ramanujan.

### Study Materials (`/studymaterials/index.html`)
- Past IMLEM meets (contest PDFs + solutions) — **external**: `http://www.matharchive.org/imlem/` and ~54 direct PDF links by season (`/imlem/2025-26/202510_imlem.pdf` pattern; one per meet, 11 seasons 2015-16 → 2025-26).
- IMLEM question bank and quiz generator — external, prepforstem.com.
- Book: *Hard Math for Middle School: IMLEM Edition* ($10) and *IMLEM Plus Edition* ($12), Glenn Ellison — Amazon links.
- Video playlists by Noah Abji for Meets 1–5 — YouTube (5 playlists).
- Lexington Clarke Middle School old study materials — web.archive.org snapshot.

### League Information (`/leagueinfo/`)
- `/leagueinfo/index.html` — lists officers 2015-16 → 2018-19 (pages exist through 2022-23 but are not linked).
- `/leagueinfo/YYYYYY/…officers.html` for 2015-16 → 2022-23 (8 pages): elected officers (President, Treasurer, Contest Writer, Tabulator) and cluster coordinators with school.
- `/leagueinfo/bylaws/2003bylaws.html` — **League Bylaws, March 2003**: team make-up, test description (six categories), team roster, meet procedures, personnel/duties, league organization, host duties, officers, awards. 20 KB, authoritative rules text.

### Contact (`/contact/`)
- `president.html`, `tabulator.html`, `treasurer.html`, `contestwriter.html` — postal address plus an obfuscated email pattern (`kelly_LASTNAME@wayland.k12.ma.us`, "replace LASTNAME"). **No full email addresses are published, deliberately.**
- `whotocontact.html` — routing table: joining/policies/dates & sites/hosting/division classification/other → President; statistics or website problems → Tabulator; dues/reimbursements → Treasurer; contest questions → Contest Writer.

### Links (`/links/index.html`)
Five sections: Other math leagues in Massachusetts; Math leagues near Massachusetts with websites; Regional/national competitions; Nearby enrichment programs; Summer math camps. About 35 external sites (e.g. MAML, ARML, MATHCOUNTS, AMC, PUMaC, Mandelbrot, Math Kangaroo, PROMYS, Mathcamp).

### Coaches' Corner (`/coaches/`)
HTTP 401 — **not audited**. See open questions.

### Assets and misc
`favicon.ico`, `imlem.css`, `sorttable.js`, `logos/50th_anniversary.gif`, `*/pdf.gif`.

## Broken links on the old site

| From | Broken target |
|---|---|
| `/meetinfo/202425/202425datessites.html` | `201819topics.html#1…#5` (404) |
| `/meetinfo/202425/` | `201819topics.html`, `201819datessites.html`, `201718datessites.html` (404) |
| `/meetinfo/201819/` | `201718datessites.html` (404) |
| `/meetinfo/202021/` | `201819datessites.html`, `201920datessites.html` (404) |
| Homepage (commented out) | `/directions/index.html` |

## Coverage matrix (what exists per season)

| Season | Dates/sites | Topics | Clusters | Individual | Team (division) | Team (overall) | Officers | Contest PDFs (matharchive) |
|---|---|---|---|---|---|---|---|---|
| 2015-16 | ✓ | ✓ (+PDF) | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| 2016-17 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| 2017-18 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| 2018-19 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| 2019-20 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 4 |
| 2020-21 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| 2021-22 | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | 5 |
| 2022-23 | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | 5 |
| 2023-24 | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | 5 |
| 2024-25 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | "Pending" | 4 |
| 2025-26 | — | ✓ | — | ✓ | ✓ | ✓ | — | 5 |
| 2026-27 | — | ✓ | — | — | — | — | — | — |

The counts in the last column are the matharchive.org links the old site references (some meets, e.g. 2019-20 and 2024-25, link four rather than five).

## External dependencies of the old site

matharchive.org (contest PDFs — 54 links), prepforstem.com, Amazon, YouTube (Noah Abji playlists), web.archive.org, artofproblemsolving.com (Massachusetts forum), and the ~35 league/competition/camp sites on the Links page.

## Forms, downloads, interactivity

| Kind | Present on old site? |
|---|---|
| Registration / sign-up form | **No** (joining is by contacting the President) |
| Search | **No** |
| Login | Only Coaches' Corner (HTTP basic auth) |
| File downloads | One PDF (2015-16 topics); contest PDFs live on matharchive.org |
| Sortable tables | Yes (sorttable.js) on all statistics tables |
| Calendar / countdown / announcements | No |
