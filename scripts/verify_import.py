"""Cross-check data/imlem.sqlite against the archive: every data row must be present.

Counts <tr> rows containing <td> in each statistics file and compares with the
database. Exits non-zero on any mismatch. Used by the test suite too.
"""
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def data_rows(path):
    html = path.read_bytes().decode('utf-8', 'replace')
    return sum(1 for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I) if '<td' in tr.lower() and '<th' not in tr.lower())


def check(archive=ROOT / 'archive' / 'imlem.org', db_path=ROOT / 'data' / 'imlem.sqlite'):
    db = sqlite3.connect(db_path)
    problems = []
    for (season,) in db.execute('SELECT id FROM seasons ORDER BY id'):
        code = season.replace('-', '')
        d = archive / 'statistics' / code
        if not d.exists():
            continue
        want = data_rows(d / f'{code}_individual.html')
        got = db.execute('SELECT COUNT(*) FROM individuals WHERE season=?', (season,)).fetchone()[0]
        if want != got:
            problems.append(f'{season} individuals: html {want} vs db {got}')
        want = data_rows(d / f'{code}_team.html')
        got = db.execute("SELECT COUNT(*) FROM teams WHERE season=? AND scope='overall'", (season,)).fetchone()[0]
        if want != got:
            problems.append(f'{season} overall teams: html {want} vs db {got}')
        want = data_rows(d / f'{code}_team_bydivision.html')
        got = db.execute("SELECT COUNT(*) FROM teams WHERE season=? AND scope<>'overall'", (season,)).fetchone()[0]
        if want != got:
            problems.append(f'{season} by-division teams: html {want} vs db {got}')
    return problems


if __name__ == '__main__':
    probs = check()
    print('\n'.join(probs) if probs else 'import verified: every archived result row is in the database')
    sys.exit(1 if probs else 0)
