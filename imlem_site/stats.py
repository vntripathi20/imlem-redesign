"""Derived statistics for the results archive: schools, season summaries and league records.

Everything here is computed from the imported results (``teams`` and ``individuals``); nothing is
typed in by hand. Facts the code relies on, checked against every row of the archive:

* A team's season total is the sum of its meet scores (806 of 806 overall rows).
* A student's season total drops their lowest meet: best four of five meets, or best three of four
  in 2019-20 (12,337 of 12,337 rows). ``total5`` is the sum of every meet.

Student names never appear in anything this module returns for public pages; only counts do.
"""
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache

from . import db as D

# A school can enter more than one team (League Bylaws, section I). The results name them
# "<School> 2", "<School> 3" or "<School> A/B"; students are always listed under the school name.
_TEAM_SUFFIX = re.compile(r'\s+(?:[2-9]|[AB])$')

MAX_TEAM_MEET = 216        # League Bylaws, section III
MAX_STUDENT_MEET = 18      # League Bylaws, section III


def school_of(team_name):
    """The school a team belongs to: 'Lexington Diamond 2' -> 'Lexington Diamond'."""
    return _TEAM_SUFFIX.sub('', team_name).strip()


_DIV_RANK = re.compile(r'-T?(\d+)$')


def div_place(div_rank):
    """'Pyt-3' -> 3. The results code a team's place in its division this way; the rank column of the
    division tables holds the league-wide rank."""
    m = _DIV_RANK.search(div_rank or '')
    return int(m.group(1)) if m else None


def slugify(name):
    s = name.lower().replace('&', ' and ').replace("'", '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def _scores(row):
    return [s for s, _r in json.loads(row['scores'])]


def _db_key():
    # Cache per database file (tests build their own); the data is read-only while the app runs.
    from flask import current_app
    return str(current_app.config['DB_PATH'])


# --------------------------------------------------------------------------- schools

@lru_cache(maxsize=8)
def _schools(db_key):
    teams = D.q("SELECT season, school, rank_n, rank, div_rank, cluster, scores, total FROM teams "
                "WHERE scope='overall' ORDER BY season, seq")
    by_school = defaultdict(lambda: {'teams': set(), 'seasons': set(), 'rows': []})
    for t in teams:
        name = school_of(t['school'])
        s = by_school[name]
        s['teams'].add(t['school'])
        s['seasons'].add(t['season'])
        s['rows'].append(t)
    out = {}
    for name, s in by_school.items():
        main = [r for r in s['rows'] if r['school'] == name]
        best = min((r for r in s['rows'] if r['rank_n']), key=lambda r: (r['rank_n'], r['season']), default=None)
        seasons = sorted(s['seasons'])
        out[slugify(name)] = {
            'slug': slugify(name), 'name': name,
            'teams': sorted(s['teams'], key=lambda n: (n != name, n)),
            'seasons': seasons, 'first': seasons[0], 'last': seasons[-1],
            'best_rank': best['rank_n'] if best else None, 'best_season': best['season'] if best else None,
            'latest_rank': (main[-1]['rank_n'] if main and main[-1]['season'] == seasons[-1] else None),
        }
    return out


def schools():
    return sorted(_schools(_db_key()).values(), key=lambda s: s['name'].lower())


def school_by_slug(slug):
    return _schools(_db_key()).get(slug)


def school_slug_for_team(team_name):
    return slugify(school_of(team_name))


def school_history(school):
    """One entry per team per season, newest first, with division placing and student counts."""
    names = school['teams']
    marks = ','.join('?' * len(names))
    overall = D.q(f"SELECT * FROM teams WHERE scope='overall' AND school IN ({marks}) ORDER BY season DESC, seq", *names)
    divs = {(r['season'], r['school']): r for r in
            D.q(f"SELECT season, school, scope FROM teams WHERE scope<>'overall' AND school IN ({marks})", *names)}
    counts = {r['season']: r for r in D.q(
        "SELECT season, COUNT(*) AS n, SUM(CASE WHEN name<>'' THEN 1 ELSE 0 END) AS named "
        "FROM individuals WHERE school=? GROUP BY season", school['name'])}
    field = {r['season']: r['n'] for r in D.q("SELECT season, COUNT(*) AS n FROM teams WHERE scope='overall' GROUP BY season")}
    out = []
    for r in overall:
        sc = _scores(r)
        d = divs.get((r['season'], r['school']))
        out.append({
            'season': r['season'], 'team': r['school'], 'rank': r['rank'], 'rank_n': r['rank_n'],
            'of': field.get(r['season']), 'cluster': r['cluster'], 'total': r['total'],
            'division': d['scope'] if d else None, 'div_rank': r['div_rank'],
            'div_rank_n': div_place(r['div_rank']),
            'scores': sc, 'best_meet': max((s for s in sc if s is not None), default=None),
            'students': counts[r['season']]['n'] if r['school'] == school['name'] and r['season'] in counts else None,
        })
    return out


def school_honours(history):
    """Counts the page states as facts: league top-three finishes and division wins."""
    main = [h for h in history]
    return {
        'league_titles': [h['season'] for h in main if h['rank_n'] == 1],
        'podiums': [h for h in main if h['rank_n'] and h['rank_n'] <= 3],
        'division_wins': [h for h in main if h['div_rank_n'] == 1],
    }


# --------------------------------------------------------------------------- seasons

def season_overview(season):
    overall = D.q("SELECT * FROM teams WHERE season=? AND scope='overall' ORDER BY seq", season)
    if not overall:
        return None
    n_meets = len(json.loads(overall[0]['scores']))
    podium = [dict(r) for r in overall if r['rank_n'] and r['rank_n'] <= 3]
    division_winners = []
    for d in D.season_divisions(season):
        rows = D.q("SELECT * FROM teams WHERE season=? AND scope=? ORDER BY seq", season, d)
        winners = [r for r in rows if div_place(r['div_rank']) == 1]
        if winners:
            division_winners.append({'division': d, 'teams': [dict(w) for w in winners], 'size': len(rows)})

    meets = []
    for i in range(n_meets):
        vals = [(s, r['school']) for r in overall for s in [_scores(r)[i]] if s is not None]
        if not vals:
            continue
        top = max(v for v, _ in vals)
        meets.append({
            'number': i + 1, 'teams': len(vals), 'average': round(sum(v for v, _ in vals) / len(vals), 1),
            'high': top, 'high_teams': [n for v, n in vals if v == top],
        })

    ind = D.q("SELECT grade, meet_totals, total FROM individuals WHERE season=?", season)
    grades = Counter(r['grade'] for r in ind)
    perfect_meets = [0] * n_meets
    for r in ind:
        for i, t in enumerate(json.loads(r['meet_totals'])):
            if t == MAX_STUDENT_MEET:
                perfect_meets[i] += 1
    counting = n_meets - 1
    perfect_season = sum(1 for r in ind if r['total'] == MAX_STUDENT_MEET * counting)

    prev = previous_season(season)
    gains = []
    if prev:
        before = {r['school']: r for r in D.q("SELECT * FROM teams WHERE season=? AND scope='overall'", prev)}
        prev_meets = len(json.loads(next(iter(before.values()))['scores'])) if before else 0
        for r in overall:
            p = before.get(r['school'])
            # Only full seasons compare fairly; a missed meet would look like a big drop or gain.
            if p and prev_meets == n_meets and None not in _scores(r) and None not in _scores(p):
                gains.append({'school': r['school'], 'gain': r['total'] - p['total'], 'total': r['total'], 'before': p['total']})
        gains.sort(key=lambda g: -g['gain'])
    return {
        'season': season, 'n_meets': n_meets, 'teams': len(overall), 'students': len(ind),
        'schools': len({school_of(r['school']) for r in overall}),
        'podium': podium, 'division_winners': division_winners, 'meets': meets,
        'grades': sorted(grades.items()), 'perfect_meets': perfect_meets, 'perfect_season': perfect_season,
        'counting_meets': counting, 'previous': prev, 'gains': [g for g in gains[:5] if g['gain'] > 0],
    }


def previous_season(season):
    seasons = D.results_seasons()  # newest first
    i = seasons.index(season) if season in seasons else -1
    return seasons[i + 1] if 0 <= i < len(seasons) - 1 else None


# --------------------------------------------------------------------------- records

@lru_cache(maxsize=8)
def _records(db_key):
    overall = D.q("SELECT * FROM teams WHERE scope='overall'")
    seasons = sorted({r['season'] for r in overall})
    n_meets = {s: len(json.loads(next(r for r in overall if r['season'] == s)['scores'])) for s in seasons}

    season_totals = sorted((r for r in overall if n_meets[r['season']] == 5),
                           key=lambda r: (-r['total'], r['season']))[:10]
    meet_scores = []
    for r in overall:
        for i, s in enumerate(_scores(r)):
            if s is not None:
                meet_scores.append({'score': s, 'school': r['school'], 'season': r['season'], 'meet': i + 1})
    meet_scores.sort(key=lambda m: (-m['score'], m['season'], m['meet']))
    top_meets = [m for m in meet_scores if m['score'] >= meet_scores[min(9, len(meet_scores) - 1)]['score']]

    titles = Counter(school_of(r['school']) for r in overall if r['rank_n'] == 1)
    podiums = Counter(school_of(r['school']) for r in overall if r['rank_n'] and r['rank_n'] <= 3)
    div_wins = Counter(school_of(r['school']) for r in overall if div_place(r['div_rank']) == 1)
    champions = [{'season': s, 'teams': [r['school'] for r in overall if r['season'] == s and r['rank_n'] == 1]}
                 for s in reversed(seasons)]

    participation = []
    for s in seasons:
        rows = [r for r in overall if r['season'] == s]
        students = D.q1('SELECT COUNT(*) AS n FROM individuals WHERE season=?', s)['n']
        perfect = 0
        for r in D.q('SELECT meet_totals FROM individuals WHERE season=?', s):
            perfect += sum(1 for t in json.loads(r['meet_totals']) if t == MAX_STUDENT_MEET)
        participation.append({'season': s, 'teams': len(rows), 'schools': len({school_of(r['school']) for r in rows}),
                              'students': students, 'perfect': perfect, 'meets': n_meets[s],
                              'average': round(sum(r['total'] for r in rows) / len(rows) / n_meets[s], 1)})
    return {
        'season_totals': [dict(r) for r in season_totals], 'top_meets': top_meets,
        'titles': titles.most_common(), 'podiums': podiums.most_common(10), 'division_wins': div_wins.most_common(10),
        'champions': champions, 'participation': participation, 'first': seasons[0], 'last': seasons[-1],
        'perfect_216': [m for m in meet_scores if m['score'] == MAX_TEAM_MEET],
    }


def records():
    return _records(_db_key())


# --------------------------------------------------------------------------- study topics

def topic_guide(category):
    """Every published topic line for one round subject, grouped by identical wording."""
    rows = D.q("SELECT r.season, r.meet, r.description, m.contest_url, m.date_text FROM rounds r "
               "JOIN meets m ON m.season=r.season AND m.number=r.meet "
               "WHERE r.category=? AND r.label LIKE 'Round%' ORDER BY r.season DESC, r.meet", category)
    groups = defaultdict(list)
    for r in rows:
        key = re.sub(r'\s+', ' ', (r['description'] or '').strip().rstrip('.'))
        groups[key].append(dict(r))
    out = [{'topic': k, 'uses': v, 'count': len(v), 'latest': v[0]['season']} for k, v in groups.items() if k]
    out.sort(key=lambda g: (-g['count'], g['topic'].lower()))
    return out, len(rows)
