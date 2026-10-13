# IMLEM website

The site for the Intermediate Math League of Eastern Massachusetts: contest dates and round topics, a results archive (11 seasons, filterable and searchable), study materials, league information and contact details. It replaces the old static site at imlem.org and keeps every old URL working through redirects.

Server-rendered Flask, no JavaScript required (small scripts add sorting, filtering and a countdown). Results are stored in SQLite, generated from the untouched copy of the old site in `archive/`.

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
| `imlem_site/legacy.py` | Old imlem.org path to new URL mapping (drives all redirects) |
| `imlem_site/importer.py`, `scripts/import_archive.py` | Builds `data/imlem.sqlite` from `archive/` without modifying it |
| `imlem_site/sanitize.py` | Cleans migrated old pages (allow-list, link rewriting) |
| `scripts/verify_import.py` | Proves every archived result row reached the database |
| `archive/imlem.org/` | **Byte-for-byte copy of the old site (253 files). Never edit.** `archive/*.json` hold the crawl's link graph and errors |
| `data/announcements.json`, `data/resources.json`, `data/study-materials.json` | Editable content |
| `templates/`, `static/` | Pages, CSS, JavaScript |
| `files/`, `uploads/` | PDFs hosted by this site |
| `images/` | Old π logo, 50th-anniversary mark, earlier clip art, and stock photos (two are used on the home page as placeholders) |
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

## Privacy and indexing

Individual results, student pages and student search show first name + last initial, grade and school, as the old site did (and only for some students). Pending league approval, those pages are `noindex` and are left out of `sitemap.xml`. Team and school pages are indexable. The switch lives in `imlem_site/config.py`.

## Known gaps

See [docs/pending-league-decisions.md](docs/pending-league-decisions.md): Coaches' Corner, current officers, student-name approval, and the 50th-anniversary history.

## Credits

`images/icons/` is CC0 clip art from openclipart.org; `images/banner/` are Pexels-licensed stock photos (not IMLEM photos). The 50th-anniversary mark and the old π favicon come from IMLEM.

The home page shows two of the stock photos as placeholders (`HOME_PHOTOS` in `imlem_site/config.py`). Replace them with photos from real meets once the league approves photo use, or set an entry to `None` to show no photo.

The header mark and favicon (`static/img/imlem-cube.*`) are a single cube drawn for this site after the cubes in the 50th-anniversary mark. Headings use TeX Gyre Adventor, subset to Latin in `static/fonts/`, under the GUST Font License (`static/fonts/GUST-FONT-LICENSE.txt`).
