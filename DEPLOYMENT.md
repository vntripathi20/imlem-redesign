# Deployment Runbook

This app has no separate database — `data/*.json` and `uploads/` are the entire dataset. Treat them accordingly: back them up, and don't lose the host they live on.

## 1. Required environment variables

| Variable | Required | Purpose |
|---|---|---|
| `IMLEM_SECRET_KEY` | Yes, unless `FLASK_DEBUG=1` | Signs session cookies. The app refuses to start without it outside debug mode. |
| `FLASK_DEBUG` | No (default off) | Set to `1` only for local development. Never set in production — it enables the interactive debugger and disables the `Secure` cookie flag. |
| `PORT` | No (default `5000`) | Port the dev server binds to. Most hosting platforms set this for you. |

Generate a secret key once and store it with your host's secret manager (not in git):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. Running it

**Local development** (debug on, relaxed cookies, auto-reload):

```powershell
$env:FLASK_DEBUG = "1"
py app.py
```

**Production-style run** (no debug, real secret key, served by Waitress instead of Flask's dev server):

```powershell
$env:IMLEM_SECRET_KEY = "<your generated key>"
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

On Linux hosting, `gunicorn` is the equivalent:

```bash
IMLEM_SECRET_KEY="<your generated key>" gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Either way, put a real reverse proxy / load balancer in front (nginx, Caddy, or whatever your host provides) to terminate HTTPS. Flask itself is not doing TLS.

## 3. HTTPS is required for login to work in production

With `FLASK_DEBUG` unset, `SESSION_COOKIE_SECURE` is automatically `True`, meaning the browser will only send the session cookie over HTTPS. If you deploy behind plain HTTP, login will appear to "do nothing" (the cookie just won't stick). Get HTTPS terminated at your reverse proxy/host before testing login on the deployed URL.

## 4. Before going live: rotate the seeded credentials

The app ships with two seed accounts (see `data/users.json`):

- `admin@imlem.org` / `admin123`
- `coach@imlem.org` / `coach123`

These passwords have been typed into chat and exist in git history — **do not leave them active on a public deployment.** There's no self-service password-change UI yet, so rotate them manually:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-new-password'))"
```

Paste the resulting hash into the matching account's `passwordHash` field in `data/users.json`, then restart the app.

## 5. Back up `data/` and `uploads/` regularly

There is no database to restore from if these are lost — they *are* the database. Zip both directories on a schedule (cron, your host's backup feature, or even a manual habit before any major change) and keep copies somewhere other than the same host.

## 6. Review real content before IMLEM staff start using it

Double check `data/divisions.json` for any divisions/schools left over from development/testing that shouldn't be on the live site, and confirm the meet schedule in `data/meets.json` reflects the real season.

## 7. Day-to-day usage needs no server access

Once deployed, IMLEM's admin and coaches only need the site URL and their login credentials — everything else (creating divisions/schools/coach accounts, recording scores, uploading study materials, editing rosters) happens through the Admin/Coach dashboards in the browser. No one but you needs shell or host access.
