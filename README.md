# IMLEM website

The site for the Intermediate Math League of Eastern Massachusetts: contest dates and round topics (with calendar downloads), a results archive (11 seasons, with school histories, season summaries and league records), a plain-language guide to how meets work, study materials organized by meet, league information and contact details. It replaces the old static site at imlem.org and keeps every old URL working through redirects.

Server-rendered Flask, no JavaScript required (small scripts add table sorting and filtering, the mobile menu, and chart tooltips). Results are stored in SQLite, generated from the untouched copy of the old site in `archive/`.

## Run it locally

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements-dev.txt
$env:FLASK_DEBUG = "1"
.\.venv\Scripts\python app.py
```

Open <http://127.0.0.1:5000>. On first start the app builds `data/imlem.sqlite` from `archive/` (a few seconds). On Linux/macOS use `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && FLASK_DEBUG=1 .venv/bin/python app.py`.

Run the tests: `.\.venv\Scripts\python -m pytest`

Deploying: see [DEPLOYMENT.md](DEPLOYMENT.md).

## Layout

| Path | What it is |
|---|---|
| `app.py` | Entry point (`app:app` for gunicorn/waitress) |
| `imlem_site/web.py` | Routes, security headers, sitemap/robots |
| `imlem_site/explore.py` | Schools, records, meet guide, calendar files, practice pages, season switcher |
| `imlem_site/stats.py` | Everything computed from the results: school histories, season summaries, records |
| `imlem_site/charts.py` | Small server-rendered SVG charts (rank by season, columns by season) |
| `imlem_site/legacy.py` | Old imlem.org path to new URL mapping (drives all redirects) |
| `imlem_site/importer.py`, `scripts/import_archive.py` | Builds `data/imlem.sqlite` from `archive/` without modifying it |
| `imlem_site/sanitize.py` | Cleans migrated old pages (allow-list, link rewriting) |
| `scripts/verify_import.py` | Proves every archived result row reached the database |
| `archive/imlem.org/` | **Byte-for-byte copy of the old site (253 files). Never edit.** `archive/*.json` hold the crawl's link graph and errors |
| `data/announcements.json`, `data/resources.json`, `data/study-materials.json` | Editable content |
| `templates/`, `static/` | Pages, CSS, JavaScript |
| `files/`, `uploads/` | PDFs hosted by this site |
| `images/` | π logo, 50th-anniversary mark, earlier clip art, and stock photos (two are used on the home page as placeholders) |
| `tests/` | pytest suite |
| `docs/` | Site inventory, gap analysis, pending league decisions |

## URL map (old to new)

| Old | New |
|---|---|
| `/statistics/YYYYYY/YYYYYY_team.html` | `/results/YYYY-YY/teams/` |
| `/statistics/YYYYYY/YYYYYY_team_bydivision.html` | `/results/YYYY-YY/divisions/` |
| `/statistics/YYYYYY/YYYYYY_individual.html` | `/results/YYYY-YY/individuals/` |
| `/meetinfo/YYYYYY/YYYYYYtopics.html` | `/contests/YYYY-YY/topics/` |
| `/meetinfo/YYYYYY/YYYYYYdatessites.html` | `/contests/YYYY-YY/dates/` |
| `/meetinfo/YYYYYY/cluster/N.html` | `/contests/YYYY-YY/clusters/N/` |
| `/leagueinfo/...officers.html`, `/leagueinfo/bylaws/...` | `/about/officers/YYYY-YY/`, `/about/bylaws/` |
| `/studymaterials/`, `/contact/...`, `/links/`, `/coaches/` | `/study/`, `/contact/...`, `/links/`, `/coaches/` |

`tests/test_legacy_redirects.py` requests every URL the old site served and fails if any does not end on a working page.

## Pages built from the results

| Page | What it shows |
|---|---|
| `/schools/`, `/schools/<name>/` | Every school; each school's teams with league and division finish, meet scores and totals by season, and a chart of its league finish. A school's second teams (`Lexington Diamond 2`) share its page. |
| `/results/YYYY-YY/` | The top three, each division's winner, meet-by-meet averages and high scores, perfect individual meets, biggest gains on the previous season |
| `/results/records/` | League champions, most titles and division wins, highest season totals and meet scores, participation and scoring by season |
| `/about/how-meets-work/` | Teams, rounds, scoring, calculators, meet day, clusters and divisions, awards, appeals; each section names the Bylaws section it summarizes |
| `/study/` and `/study/meet/<n>/` | A topic map of the season, and for each meet its topics plus every past contest for that meet |
| `/contests/YYYY-YY/calendar.ics` | The season's meets as all-day calendar events |

Facts these pages state are checked against the data in `tests/test_explore.py`: a team's season total is the sum of its meets; a student's season total drops their lowest meet (best four of five; best three of four in 2019-20); and each meet's round topics have been identical every season since 2015-16. Division places come from the results' division codes (`Pyt-3` is 3rd in Pythagoras); the rank column in the division tables is the league-wide rank. These pages use counts only, never student names.

## Privacy and indexing

Individual results, student pages and student search show first name + last initial, grade and school, as the old site did (and only for some students). Pending league approval, those pages are `noindex` and are left out of `sitemap.xml`. Team and school pages are indexable. The switch lives in `imlem_site/config.py`.

## Known gaps

See [docs/pending-league-decisions.md](docs/pending-league-decisions.md): Coaches' Corner, current officers, student-name approval, and the 50th-anniversary history.

## Credits

`images/icons/` is CC0 clip art from openclipart.org; `images/banner/` are Pexels-licensed stock photos (not IMLEM photos). The π logo (based on the old site's favicon) and the 50th-anniversary mark come from IMLEM.

The home page shows two of the stock photos as placeholders (`HOME_PHOTOS` in `imlem_site/config.py`). Replace them with photos from real meets once the league approves photo use, or set an entry to `None` to show no photo.

Headings use TeX Gyre Schola (the TeX project's Century Schoolbook), subset to Latin in `static/fonts/`, under the GUST Font License (`static/fonts/GUST-FONT-LICENSE.txt`). The six-colour stripe under each title band uses the cube colours of the 50th-anniversary mark, one per round, and the faint cube texture on the home page bands (`static/img/cube-lattice.svg`) was drawn for this site after the same mark.
