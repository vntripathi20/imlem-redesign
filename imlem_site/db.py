"""Read-only access to data/imlem.sqlite (built from the archive on first start)."""
import json
import sqlite3
from datetime import date

from flask import current_app, g

from .importer import IMPORT_VERSION, build_database


def _built_version(path):
    try:
        with sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True) as db:
            return db.execute('PRAGMA user_version').fetchone()[0]
    except sqlite3.Error:
        return None


def ensure_database(app):
    """Build the database if it is missing or was made by an older importer."""
    path = app.config['DB_PATH']
    if not path.exists() or _built_version(path) != IMPORT_VERSION:
        app.logger.info('Building %s from %s', path, app.config['ARCHIVE_DIR'])
        build_database(app.config['ARCHIVE_DIR'], path)


def get_db():
    if 'db' not in g:
        path = current_app.config['DB_PATH']
        g.db = sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def q(sql, *args):
    return get_db().execute(sql, args).fetchall()


def q1(sql, *args):
    return get_db().execute(sql, args).fetchone()


def like(term):
    """Escape a user string for LIKE ... ESCAPE '\\' (substring match)."""
    return '%' + term.replace('\\', '\\\\').replace('%', r'\%').replace('_', r'\_') + '%'


# -- seasons -----------------------------------------------------------------

def seasons():
    return [r['id'] for r in q('SELECT id FROM seasons ORDER BY start_year DESC')]


def results_seasons():
    return [r['season'] for r in q('SELECT DISTINCT season FROM individuals ORDER BY season DESC')]


def season_summary(season):
    row = q1('SELECT * FROM seasons WHERE id=?', season)
    if not row:
        return None
    return {
        'id': season,
        'has_topics': bool(q1('SELECT 1 FROM meets WHERE season=?', season)),
        'has_dates': bool(q1("SELECT 1 FROM pages WHERE kind='dates' AND key=?", season)),
        'has_clusters': bool(q1("SELECT 1 FROM pages WHERE kind='clusters' AND key=?", season)),
        'has_results': bool(q1('SELECT 1 FROM individuals WHERE season=?', season)),
        'has_officers': bool(q1("SELECT 1 FROM pages WHERE kind='officers' AND key=?", season)),
    }


def neighbours(season, available):
    """Previous/next season ids inside ``available`` (a newest-first list)."""
    if season not in available:
        return None, None
    i = available.index(season)
    newer = available[i - 1] if i > 0 else None
    older = available[i + 1] if i + 1 < len(available) else None
    return older, newer


def page(kind, key):
    return q1('SELECT * FROM pages WHERE kind=? AND key=?', kind, key)


# -- meets -------------------------------------------------------------------

def next_meet(today=None):
    today = (today or date.today()).isoformat()
    return q1('SELECT * FROM meets WHERE date_iso >= ? ORDER BY date_iso LIMIT 1', today)


def meets_for(season):
    return q('SELECT * FROM meets WHERE season=? ORDER BY number', season)


def meet_labels(season, source):
    rows = q('SELECT meet, label FROM meet_labels WHERE season=? AND source=? ORDER BY meet', season, source)
    return {r['meet']: r['label'] for r in rows}


def season_divisions(season):
    rows = q("SELECT scope FROM teams WHERE season=? AND scope<>'overall' GROUP BY scope ORDER BY MIN(id)", season)
    return [r['scope'] for r in rows]


def decode_json_columns(row, *cols):
    d = dict(row)
    for c in cols:
        d[c] = json.loads(d[c])
    return d
