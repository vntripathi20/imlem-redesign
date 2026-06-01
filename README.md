# IMLEM Website Redesign

A Python-backed academic archive system for the Intermediate Math League of Eastern Massachusetts.

## What is included

- Python Flask backend
- Static frontend served by Flask
- Study materials archive by year and meet
- Meet information management
- Admin/coordinator dashboard workflows
- File-based JSON storage for archive data
- PDF upload support with year/meet/type assignment

## Quick start

1. Install Python dependencies

```powershell
py -m pip install -r requirements.txt
```

2. Start the application

```powershell
py app.py
```

3. Open the site at `http://localhost:5000`

## Folder layout

- `app.py` — Flask backend and API service
- `templates/` — HTML template for the frontend
- `static/` — frontend CSS and JavaScript assets
- `data/` — JSON content storage for archive, meets, clusters, statistics, and users
- `uploads/` — PDF uploads served by Flask

## Notes

- Historical study materials remain in `data/study-materials.json` and `uploads/`
- The Flask backend appends new meet and file entries, preserving past records
- Coordinators can update assigned cluster meet details without code edits
