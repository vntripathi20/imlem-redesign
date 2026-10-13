"""Schools, season summaries, records, the meet guide, calendars, practice pages and search.

Several pages state facts worked out from the results (how season totals are added up, that each
meet's topics repeat every season). The first tests check those facts against the data, so the
pages stop being true only if a test fails first.
"""
import json
import re
import sqlite3

import pytest


def _db(app):
    con = sqlite3.connect(app.config['DB_PATH'])
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------- facts the pages state

def test_team_season_total_is_the_sum_of_meets(app):
    for r in _db(app).execute("SELECT scores, total FROM teams WHERE scope='overall'"):
        assert sum(s for s, _ in json.loads(r['scores']) if s is not None) == r['total']


def test_student_season_total_drops_the_lowest_meet(app):
    for r in _db(app).execute('SELECT meet_totals, total, total5 FROM individuals'):
        meets = json.loads(r['meet_totals'])
        played = [m for m in meets if m is not None]
        assert r['total'] == sum(sorted(played, reverse=True)[:len(meets) - 1])
        assert r['total5'] in (None, sum(played))


def test_each_meets_topics_are_the_same_every_season(app):
    seen = {}
    for r in _db(app).execute("SELECT meet, category, description FROM rounds WHERE label LIKE 'Round%'"):
        seen.setdefault((r['meet'], r['category']), set()).add(r['description'])
    assert seen and all(len(v) == 1 for v in seen.values())


# ---------------------------------------------------------------- schools

def test_schools_index_lists_every_school(client):
    html = client.get('/schools/').get_data(as_text=True)
    assert html.count('href="/schools/') >= 100
    assert 'Lexington Diamond 2' not in html.split('<tbody>', 1)[1].split('</tbody>')[0].replace('(2 teams)', '')


def test_school_page_counts_titles_and_reads_division_codes(client):
    clarke = client.get('/schools/lexington-clarke/').get_data(as_text=True)
    assert 'League championships</dt><dd>8' in clarke
    assert '<svg class="chart"' in clarke and 'noindex' not in clarke
    diamond = client.get('/schools/lexington-diamond/').get_data(as_text=True)
    assert 'Lexington Diamond 2' in diamond                       # second team shares the school's page
    row = diamond.split('2025-26</a></th>', 1)[1].split('</tr>', 1)[0]
    assert 'Pythagoras' in row and '3rd' in row and '9th' in row  # 3rd in division, 9th in the league


def test_old_school_url_redirects(client):
    r = client.get('/results/school/?name=Lexington+Diamond+2')
    assert r.status_code == 301 and r.headers['Location'].endswith('/schools/lexington-diamond/')
    assert client.get('/results/school/?name=Nope+School').status_code == 404
    assert client.get('/schools/nope-school/').status_code == 404


# ---------------------------------------------------------------- seasons and records

def test_season_overview_has_podium_and_every_division_winner(client):
    html = client.get('/results/2025-26/').get_data(as_text=True)
    podium = html.split('class="podium"', 1)[1].split('</ol>', 1)[0]
    assert podium.index('Newton Brown') < podium.index('Lexington Clarke') < podium.index('Newton Oak Hill')
    winners = html.split('id="h-div"', 1)[1].split('</table>', 1)[0]
    assert winners.count('<tr>') == 12                            # header + 11 divisions
    assert 'Newton Oak Hill' in winners and 'Tewksbury Wynn' in winners
    assert 'Meet 5' in html and 'Biggest gains over 2024-25' in html


def test_four_meet_season_summary(client):
    html = client.get('/results/2019-20/').get_data(as_text=True)
    assert 'in 4 meets' in html and 'all 3 meets that count' in html


def test_records(client):
    html = client.get('/results/records/').get_data(as_text=True)
    assert 'twice in the archive' in html                         # two perfect 216-point meets
    champs = html.split('id="champions"', 1)[1].split('</table>', 1)[0]
    assert champs.count('<tr>') == 12 and champs.count('Lexington Clarke') == 8
    assert html.count('<svg class="chart"') == 3


def test_summary_pages_never_name_students(client, app):
    names = [r['name'] for r in _db(app).execute("SELECT DISTINCT name FROM individuals WHERE name<>'' LIMIT 400")]
    for path in ['/results/2025-26/', '/results/records/', '/schools/lexington-clarke/', '/schools/']:
        html = client.get(path).get_data(as_text=True)
        assert not [n for n in names if f'>{n}<' in html], path


# ---------------------------------------------------------------- guide, calendar, practice

def test_guide_cites_sources_and_states_maximums(client):
    html = client.get('/about/how-meets-work/').get_data(as_text=True)
    assert html.count('class="source"') >= 8
    assert '216' in html and '>18<' in html and 'meets 4 and 5' in html
    assert 'named after' not in html


def test_calendar_file(client):
    r = client.get('/contests/2026-27/calendar.ics')
    assert r.status_code == 200 and r.headers['Content-Type'].startswith('text/calendar')
    body = r.get_data(as_text=True)
    assert body.startswith('BEGIN:VCALENDAR\r\n') and body.endswith('END:VCALENDAR\r\n')
    assert body.count('BEGIN:VEVENT') == 5 and 'DTSTART;VALUE=DATE:20261015' in body
    assert all(len(line.encode()) <= 75 for line in body.split('\r\n'))
    assert client.get('/contests/1999-00/calendar.ics').status_code == 404


@pytest.mark.parametrize('n', [1, 2, 3, 4, 5])
def test_practice_pages_list_every_past_contest(client, app, n):
    html = client.get(f'/study/meet/{n}/').get_data(as_text=True)
    urls = [r['contest_url'] for r in _db(app).execute('SELECT contest_url FROM meets WHERE number=? AND contest_url IS NOT NULL', (n,))]
    assert urls and all(u in html for u in urls)
    assert ('Calculators are allowed' in html) == (n >= 4)


def test_practice_page_range(client):
    assert client.get('/study/meet/6/').status_code == 404


def test_study_topic_map(client):
    html = client.get('/study/').get_data(as_text=True)
    grid = html.split('class="data topic-map', 1)[1].split('</table>', 1)[0]
    assert grid.count('href="/study/meet/') == 10                  # meet name and contest count, five meets
    assert 'Area and perimeter of polygons' in grid and 'Combinatorics and probability' in grid


# ---------------------------------------------------------------- search, navigation, SEO

def test_search_groups_schools_and_finds_topics(client):
    html = client.get('/results/search/?q=venn').get_data(as_text=True)
    assert '/study/meet/5/' in html
    html = client.get('/results/search/?q=diamond').get_data(as_text=True)
    assert html.count('href="/schools/lexington-diamond/"') == 1


def test_season_switcher_only_goes_to_known_pages(client):
    r = client.get('/go/?to=results_teams&season=2020-21')
    assert r.status_code == 303 and r.headers['Location'].endswith('/results/2020-21/teams/')
    assert client.get('/go/?to=calendar&season=2020-21').status_code == 404
    assert client.get('/go/?to=results_teams&season=1999-00').status_code == 404


def test_header_search_on_every_page(client):
    for p in ['/', '/study/', '/schools/']:
        assert 'id="site-q"' in client.get(p).get_data(as_text=True)


def test_sitemap_includes_new_pages_but_no_students(client):
    xml = client.get('/sitemap.xml').get_data(as_text=True)
    for p in ['/schools/', '/schools/lexington-clarke/', '/results/records/', '/about/how-meets-work/', '/study/meet/3/']:
        assert p in xml
    assert '/individuals/' not in xml and '/search/' not in xml
    assert not re.search(r'/schools/[^<]*\?', xml)
