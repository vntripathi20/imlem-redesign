"""Build data/imlem.sqlite from the untouched mirror in archive/imlem.org.

The archive is read, never written. Rebuild any time:

    python scripts/import_archive.py

Every parsing surprise is collected in ``report`` and printed, so nothing is
silently dropped.
"""
import html as htmllib
import json
import os
import re
import sqlite3
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

from . import sanitize
from .legacy import season_id

# Bump when the importer's output changes; an older data/imlem.sqlite is rebuilt automatically.
IMPORTER_VERSION = 2

SCHEMA = """
CREATE TABLE seasons (id TEXT PRIMARY KEY, code TEXT NOT NULL, start_year INTEGER NOT NULL);
CREATE TABLE individuals (
    id INTEGER PRIMARY KEY, season TEXT NOT NULL, seq INTEGER NOT NULL,
    overall_rank TEXT, overall_rank_n INTEGER, div_rank TEXT, grade_rank TEXT,
    name TEXT NOT NULL, name_lc TEXT NOT NULL, grade TEXT, school TEXT, school_lc TEXT, division TEXT,
    rounds TEXT NOT NULL,            -- JSON: 5 meets x 5 rounds (null = blank)
    meet_totals TEXT NOT NULL,       -- JSON: 5 ints/null
    total INTEGER, total5 INTEGER,
    UNIQUE (season, seq)
);
CREATE INDEX ix_ind_season ON individuals (season, division);
CREATE INDEX ix_ind_name ON individuals (name_lc);
CREATE INDEX ix_ind_school ON individuals (season, school_lc);
CREATE TABLE teams (
    id INTEGER PRIMARY KEY, season TEXT NOT NULL, scope TEXT NOT NULL,   -- 'overall' or a division name
    seq INTEGER NOT NULL, rank_n INTEGER, rank TEXT, div_rank TEXT, school TEXT NOT NULL, school_lc TEXT NOT NULL,
    cluster TEXT, scores TEXT NOT NULL,   -- JSON: 5 x [score, rank]
    total INTEGER
);
CREATE INDEX ix_team_season ON teams (season, scope);
CREATE INDEX ix_team_school ON teams (school_lc);
CREATE TABLE meet_labels (season TEXT, source TEXT, meet INTEGER, label TEXT, PRIMARY KEY (season, source, meet));
CREATE TABLE meets (
    season TEXT, number INTEGER, heading TEXT, date_text TEXT, date_iso TEXT, calculators INTEGER,
    contest_url TEXT, PRIMARY KEY (season, number)
);
CREATE TABLE rounds (season TEXT, meet INTEGER, seq INTEGER, label TEXT, category TEXT, description TEXT);
CREATE INDEX ix_rounds_cat ON rounds (category);
CREATE TABLE pages (kind TEXT, key TEXT, season TEXT, title TEXT, body TEXT, source TEXT, PRIMARY KEY (kind, key));
"""


class _Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self._t, self._row, self._cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'table':
            self._t = {'class': a.get('class', ''), 'rows': []}
            self.tables.append(self._t)
        elif tag == 'tr' and self._t is not None:
            self._row = []
            self._t['rows'].append(self._row)
        elif tag in ('td', 'th') and self._row is not None:
            self._cell = {'tag': tag, 'text': '', 'span': int(a.get('colspan', 1) or 1)}
            self._row.append(self._cell)
        elif tag == 'br' and self._cell is not None:
            self._cell['text'] += ' '

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            self._cell = None
        elif tag == 'table':
            self._t = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell['text'] += data


def _text(s):
    return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip()


def _plain(fragment):
    """Text of an HTML fragment: tags removed, entities decoded (&nbsp; -> space), whitespace collapsed."""
    return _text(htmllib.unescape(re.sub(r'<[^>]+>', '', fragment)))


def _int(s):
    s = _text(s).strip('()')
    return int(s) if re.fullmatch(r'-?\d+', s) else None


def _read(path):
    raw = Path(path).read_bytes()
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('cp1252', 'replace')


def _tables(html):
    p = _Tables()
    p.feed(html)
    return p.tables


def _meet_labels(header_row):
    labels = []
    for c in header_row:
        m = re.match(r'Meet (\d)\s*(.*)', _text(c['text']))
        if m:
            labels.append((int(m.group(1)), m.group(2)))
    return labels


def import_individuals(db, root, season, report):
    code = season.replace('-', '')
    html = _read(root / 'statistics' / code / f'{code}_individual.html')
    tables = _tables(html)
    t = next(x for x in tables if 'indiv' in x['class'])
    for meet, label in _meet_labels(t['rows'][0]):
        db.execute('INSERT INTO meet_labels VALUES (?,?,?,?)', (season, 'individual', meet, label))
    seq = 0
    for row in t['rows']:
        if any(c['tag'] == 'th' for c in row):
            continue
        cells = [_text(c['text']) for c in row]
        meets = (len(cells) - 9) / 6          # 7 id columns + 6 per meet + 2 totals
        if meets != int(meets) or not 1 <= meets <= 5:
            report.append(f'{season} individual: row with {len(cells)} cells skipped: {cells[:6]}')
            continue
        meets = int(meets)
        seq += 1
        rounds, totals = [], []
        for k in range(meets):
            base = 7 + 6 * k
            vals = []
            for v in cells[base:base + 5]:
                n = _int(v)
                if v and n is None:
                    report.append(f'{season} individual #{seq} non-numeric round score {v!r}')
                vals.append(n)
            rounds.append(vals)
            totals.append(_int(cells[base + 5]))
        total, total5 = _int(cells[-2]), _int(cells[-1])
        db.execute(
            'INSERT INTO individuals (season, seq, overall_rank, overall_rank_n, div_rank, grade_rank, name, name_lc,'
            ' grade, school, school_lc, division, rounds, meet_totals, total, total5) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (season, seq, cells[0], _int(cells[0]), cells[1], cells[2], cells[3], cells[3].lower(),
             cells[4], cells[5], cells[5].lower(), cells[6], json.dumps(rounds), json.dumps(totals), total, total5),
        )
    return seq


def _team_rows(db, season, scope, table, report):
    n = 0
    for row in table['rows']:
        if any(c['tag'] == 'th' for c in row):
            continue
        cells = [_text(c['text']) for c in row]
        meets = (len(cells) - 5) / 2          # 4 id columns + (score, rank) per meet + total
        if meets != int(meets) or not 1 <= meets <= 5:
            report.append(f'{season} team[{scope}]: row with {len(cells)} cells skipped: {cells[:5]}')
            continue
        meets = int(meets)
        n += 1
        scores = [[_int(cells[4 + 2 * k]), _int(cells[5 + 2 * k])] for k in range(meets)]
        db.execute(
            'INSERT INTO teams (season, scope, seq, rank_n, rank, div_rank, school, school_lc, cluster, scores, total)'
            ' VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (season, scope, n, _int(cells[0]), cells[0], cells[1], cells[2], cells[2].lower(), cells[3],
             json.dumps(scores), _int(cells[-1])),
        )
    return n


def import_teams(db, root, season, report):
    code = season.replace('-', '')
    overall = _tables(_read(root / 'statistics' / code / f'{code}_team.html'))[0]
    for meet, label in _meet_labels(overall['rows'][0]):
        db.execute('INSERT INTO meet_labels VALUES (?,?,?,?)', (season, 'team', meet, label))
    _team_rows(db, season, 'overall', overall, report)
    divisions = []
    for t in _tables(_read(root / 'statistics' / code / f'{code}_team_bydivision.html')):
        # A page may hold one table per division or one table with repeated header rows;
        # a header row whose first cell reads "<Name> division" starts a new division.
        scope, chunk = None, {'class': t['class'], 'rows': []}

        def flush():
            if scope and chunk['rows']:
                _team_rows(db, season, scope, chunk, report)

        for row in t['rows']:
            first = _text(row[0]['text']) if row else ''
            if row and row[0]['tag'] == 'th' and re.search(r'\sdivision$', first, re.I):
                flush()
                scope = re.sub(r'\s+division$', '', first, flags=re.I)
                chunk = {'class': t['class'], 'rows': []}
                divisions.append(scope)
            else:
                chunk['rows'].append(row)
        flush()
        if scope is None:
            report.append(f'{season} by-division: table without a division name')
    return divisions


_MEET_H2 = re.compile(r'<a name="(\d)"></a>\s*<h2>(.*?)</h2>(.*?)(?=<a name="\d"></a>|<p>\s*&nbsp;|$)', re.S)


def import_topics(db, root, season, report):
    code = season.replace('-', '')
    path = root / 'meetinfo' / code / f'{code}topics.html'
    html = _read(path)
    found = 0
    for m in _MEET_H2.finditer(html):
        number, rest = int(m.group(1)), m.group(3)
        heading = _plain(m.group(2))
        hm = re.match(r'Meet #\d -- (.*?)(?: -- (.*))?$', heading)
        date_text = hm.group(1) if hm else ''
        tag = (hm.group(2) if hm else '') or ''
        iso = None
        try:
            iso = datetime.strptime(date_text, '%B %d, %Y').date().isoformat()
        except ValueError:
            report.append(f'{season} meet {number}: unparsed date {date_text!r}')
        contest = re.search(r'href="(https?://www\.matharchive\.org/[^"]+\.pdf)"', rest)
        db.execute('INSERT INTO meets VALUES (?,?,?,?,?,?,?)', (
            season, number, heading, date_text, iso,
            0 if re.search(r'no calculators', tag, re.I) else 1,
            contest.group(1) if contest else None,
        ))
        seq = 0
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', rest, re.S):
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)
            cells = [c for c in (_plain(c) for c in cells) if c != '']
            if len(cells) < 2:
                continue
            label, topic = cells[-2], cells[-1]
            cat, _, desc = topic.partition(' -- ')
            if label.lower().startswith('team'):
                cat, desc = 'Team Round', topic
            seq += 1
            db.execute('INSERT INTO rounds VALUES (?,?,?,?,?,?)',
                       (season, number, seq, label.rstrip('.'), cat.strip(), desc.strip()))
        if seq != 6:
            report.append(f'{season} meet {number}: expected 6 round rows, found {seq}')
        found += 1
    if found != 5:
        report.append(f'{season} topics: expected 5 meets, found {found}')


def import_pages(db, root, report):
    n = 0

    def add(kind, key, season, rel):
        nonlocal n
        html = _read(root / rel)
        old = '/' + rel.replace('\\', '/')
        body = sanitize.clean(html, old, report)
        db.execute('INSERT OR REPLACE INTO pages VALUES (?,?,?,?,?,?)',
                   (kind, key, season, sanitize.title_of(html), body, old))
        n += 1

    for p in sorted((root / 'meetinfo').glob('*/*datessites.html')):
        s = season_id(p.parent.name)
        add('dates', s, s, f'meetinfo/{p.parent.name}/{p.name}')
    for p in sorted((root / 'meetinfo').glob('*/cluster/*.html')):
        s = season_id(p.parent.parent.name)
        stem = p.stem
        if stem == 'index':
            add('clusters', s, s, f'meetinfo/{p.parent.parent.name}/cluster/index.html')
        else:
            add('cluster', f'{s}/{stem}', s, f'meetinfo/{p.parent.parent.name}/cluster/{p.name}')
    for p in sorted((root / 'leagueinfo').glob('*/*officers.html')):
        s = season_id(p.parent.name)
        add('officers', s, s, f'leagueinfo/{p.parent.name}/{p.name}')
    add('bylaws', '2003', None, 'leagueinfo/bylaws/2003bylaws.html')
    for role in ('president', 'tabulator', 'treasurer', 'contestwriter'):
        add('contact', role, None, f'contact/{role}.html')
    add('who', 'who', None, 'contact/whotocontact.html')
    add('links', 'links', None, 'links/index.html')
    add('calculators', 'calculators', None, 'meetinfo/calculators.html')
    return n


def build_database(archive_dir, db_path):
    root = Path(archive_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Per-process temp file so two workers starting at once can't corrupt each other's build.
    tmp = db_path.with_suffix(f'.building.{os.getpid()}')
    tmp.unlink(missing_ok=True)
    report, summary = [], {}
    db = sqlite3.connect(tmp)
    db.executescript(SCHEMA)
    db.execute(f'PRAGMA user_version = {int(IMPORTER_VERSION)}')
    seasons =sorted({p.name for p in (root / 'statistics').iterdir() if re.fullmatch(r'\d{6}', p.name)}
                     | {p.name for p in (root / 'meetinfo').iterdir() if re.fullmatch(r'\d{6}', p.name)})
    for code in seasons:
        season = season_id(code)
        db.execute('INSERT INTO seasons VALUES (?,?,?)', (season, code, int(code[:4])))
        if (root / 'meetinfo' / code / f'{code}topics.html').exists():
            import_topics(db, root, season, report)
        if (root / 'statistics' / code / f'{code}_individual.html').exists():
            summary[season] = {
                'individuals': import_individuals(db, root, season, report),
                'divisions': import_teams(db, root, season, report),
            }
    summary['pages'] = import_pages(db, root, report)
    db.commit()
    db.close()
    tmp.replace(db_path)
    return summary, report
