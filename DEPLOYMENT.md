# Deployment

The site is a read-only Flask app. It has **no accounts, no forms, no uploads and no secrets to manage**, and it needs no database server: results live in a SQLite file that is generated from `archive/` (committed to git) the first time the app starts.

Nothing in this repository deploys the site anywhere. Pick a host from the options below when the league decides.

## What a host needs

- Python 3.10 or newer
- `pip install -r requirements.txt`
- HTTPS in front of the app (the old imlem.org's HTTPS was broken; do not repeat that). Flask does not terminate TLS itself, so use your host's HTTPS, Caddy, nginx, or a platform load balancer.
- A writable `data/` directory on first start (the SQLite file is written there once, about 10 MB, takes a few seconds). To avoid a first-request delay, run `python scripts/import_archive.py` during your build step.

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `IMLEM_SITE_URL` | derived from the request | Public base URL, e.g. `https://imlem.org`. Used for canonical links and `sitemap.xml`. Set it in production. |
| `IMLEM_TRUST_PROXY` | `0` | Set to `1` when behind a reverse proxy/load balancer so the app trusts `X-Forwarded-Proto/Host` (needed for correct HTTPS URLs and the HSTS header). |
| `IMLEM_DB` | `data/imlem.sqlite` | Location of the generated database. |
| `PORT`, `HOST` | `5000`, `127.0.0.1` | Only for `python app.py`. |
| `FLASK_DEBUG` | `0` | Local development only. Never enable in production. |
| `IMLEM_SECRET_KEY` | random per process | Not used by any current feature (the site sets no cookies). If a feature that uses sessions is ever added, set this to a fixed random value: `python -c "import secrets; print(secrets.token_hex(32))"`. |

No secret is stored in the repository.

## Running it

**Linux / macOS (any standard Python host):**

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python scripts/import_archive.py            # optional: prebuild the database
IMLEM_SITE_URL=https://imlem.org IMLEM_TRUST_PROXY=1 gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

**Windows:**

```powershell
python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt
$env:IMLEM_SITE_URL = "https://imlem.org"
.\.venv\Scripts\waitress-serve --listen=127.0.0.1:8000 app:app
```

### Hosting options

| Option | Notes |
|---|---|
| A small VPS (e.g. Ubuntu) with Caddy or nginx + gunicorn | Cheapest and simplest. Caddy gets HTTPS certificates automatically. Run gunicorn under systemd. |
| Platform-as-a-service (Render, Fly.io, Railway, Heroku-style) | Start command `gunicorn app:app`; set `IMLEM_SITE_URL` and `IMLEM_TRUST_PROXY=1`. Use a build step of `pip install -r requirements.txt && python scripts/import_archive.py`. The platform provides HTTPS. |
| Shared hosting with Python/WSGI (cPanel "Setup Python App") | Point the WSGI entry at `app:app`. Run `python scripts/import_archive.py` once from a shell. |
| Docker / any container host | Base image `python:3.12-slim`, `pip install -r requirements.txt`, `CMD gunicorn -b 0.0.0.0:8000 app:app`. |

Because the content is static between releases, you can also put a CDN in front of the app.

## Security notes

- Responses carry a strict Content-Security-Policy (`self` only), `X-Content-Type-Options`, `X-Frame-Options: DENY`, a referrer policy, and HSTS when served over HTTPS.
- The app accepts only GET/HEAD; request bodies are capped at 64 KB. There is nothing to submit, so there is no CSRF surface.
- All content pages migrated from the old site are re-serialised through an allow-list sanitizer (`imlem_site/sanitize.py`). Database queries are parameterised and read-only (`mode=ro`).
- The earlier prototype had admin and coach accounts with default passwords. That code and those accounts are gone. Those passwords exist in older git history, so never reuse them anywhere.

## Updating content

Everything is plain files in git:

| To change | Edit |
|---|---|
| Announcements on the home page | `data/announcements.json` |
| Study resources (books, videos, links) | `data/resources.json` |
| Files hosted here (PDFs) | put the PDF in `uploads/`, then add it to `data/study-materials.json` |
| Contest PDFs | They are hosted externally on matharchive.org; this site only links to them |
| New season's results, topics, dates | Add the new season's pages to `archive/imlem.org/...` in the same format and re-run `python scripts/import_archive.py`, then run `pytest` |
| Officers, contact details (**pending league confirmation**) | The migrated old pages are in the database; see `docs/pending-league-decisions.md` for how to replace them |

## Backups

`archive/`, `data/*.json` and `uploads/` are in git; the SQLite file is generated and can be rebuilt any time. Backing up the repository is enough.
