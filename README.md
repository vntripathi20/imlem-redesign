# IMLEM Website Redesign

A Python-backed academic archive system for the Intermediate Math League of Eastern Massachusetts.

## What is included

- Flask backend serving a JSON API and the frontend
- Plain HTML/CSS/JS frontend (no build step, no Node)
- Study materials archive by year and meet
- Meet information management
- Admin and coach login with role-scoped dashboards
- File-based JSON storage for archive data
- PDF upload support with year/meet/type assignment

## Quick start (local development)

1. Install Python dependencies

```powershell
py -m pip install -r requirements.txt
```

2. Start the application in debug mode

```powershell
$env:FLASK_DEBUG = "1"
py app.py
```

3. Open the site at `http://localhost:5000`

For a production-style run instead, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Folder layout

- `app.py` — Flask backend, API, and page serving
- `templates/` — HTML page shell for the frontend
- `static/` — frontend CSS and JavaScript (hash-routed single page)
- `data/` — JSON content storage for archive, meets, divisions/schools, statistics, and users
- `uploads/` — PDF uploads served by Flask
- `images/` — site images
- `images/icons/` — section icons and the hero illustration; CC0 public-domain clip art from [openclipart.org](https://openclipart.org), used as-is

## Notes

- Historical study materials remain in `data/study-materials.json` and `uploads/`
- The Flask backend appends new meet and file entries, preserving past records
- Schools live inside divisions (`data/divisions.json`); coaches log in and manage only their own school's info, roster, and view their results
- Admins create coach accounts, divisions, schools, and meets from the Admin Dashboard
