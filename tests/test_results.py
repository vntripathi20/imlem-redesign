"""Results archive: import completeness, filters, sorting, search, privacy rules."""
import re

import pytest

from scripts import verify_import  # noqa: F401  (imported so the test fails loudly if the script breaks)


def rows(html):
    return re.findall(r'<tr>\s*<td class="c-rank" data-label="Rank">', html)


def test_import_is_complete(app):
    problems = verify_import.check(app.config['ARCHIVE_DIR'], app.config['DB_PATH'])
    assert problems == []


def test_every_season_has_results_pages(client):
    for season in ['2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22',
                   '2022-23', '2023-24', '2024-25', '2025-26']:
        for view in ('teams', 'divisions', 'individuals'):
            assert client.get(f'/results/{season}/{view}/').status_code == 200, (season, view)


def test_known_values_from_archive(client):
    teams = client.get('/results/2025-26/teams/').get_data(as_text=True)
    assert 'Newton Brown' in teams and '1017' in teams            # 2025-26 rank 1, total 1017 in the archive
    assert 'Euc-1' in teams


def test_divisions_are_per_season(client):
    d2025 = client.get('/results/2025-26/divisions/').get_data(as_text=True)
    d1516 = client.get('/results/2015-16/divisions/').get_data(as_text=True)
    assert 'Ramanujan' in d2025 and 'Liu Hui' not in d2025
    assert 'Liu Hui' in d1516 and 'Lexington' in d1516
    d2021 = client.get('/results/2020-21/divisions/').get_data(as_text=True)
    assert 'Mosca' in d2021 and 'Ramanujan' not in d2021


def test_meet_count_2019_20_is_four(client):
    html = client.get('/results/2019-20/individuals/').get_data(as_text=True)
    assert 'Meet 4' in html and 'Meet 5' not in html


def test_individual_filter_by_division_and_grade(client):
    html = client.get('/results/2025-26/individuals/?division=Euclid&grade=7').get_data(as_text=True)
    assert 'data-label="Division">Euclid<' in html
    assert 'data-label="Division">Pascal<' not in html
    assert 'data-label="Gr.">8<' not in html


def test_individual_filter_by_school(client):
    html = client.get('/results/2025-26/individuals/?school=newton+oak').get_data(as_text=True)
    assert 'Newton Oak Hill' in html
    assert 'Lexington Clarke' not in html


def test_individual_filter_by_name_and_no_results_message(client):
    html = client.get('/results/2025-26/individuals/?q=Alexandra').get_data(as_text=True)
    assert 'Alexandra B.' in html
    empty = client.get('/results/2025-26/individuals/?q=zzzzqqq').get_data(as_text=True)
    assert 'No students match' in empty


def test_sorting_by_name_asc_desc(client):
    def names(url):
        html = client.get(url).get_data(as_text=True)
        return re.findall(r'data-label="Name"><a [^>]*>([^<]+)</a>', html)
    asc = [n for n in names('/results/2025-26/individuals/?q=a&sort=name&dir=asc') if n != '—']
    desc = [n for n in names('/results/2025-26/individuals/?q=a&sort=name&dir=desc') if n != '—']
    assert asc == sorted(asc, key=str.lower)
    assert desc == sorted(desc, key=str.lower, reverse=True)


def test_invalid_sort_and_page_do_not_break(client):
    assert client.get('/results/2025-26/individuals/?sort=password;drop&dir=zz&page=abc').status_code == 200
    assert client.get('/results/2025-26/individuals/?page=99999').status_code == 200


def test_pagination(client):
    p1 = client.get('/results/2025-26/individuals/').get_data(as_text=True)
    p2 = client.get('/results/2025-26/individuals/?page=2').get_data(as_text=True)
    assert len(rows(p1)) == 100 and 'Page 1 of' in p1 and 'rel="next"' in p1
    assert 'rel="prev"' in p2


def test_sql_injection_attempts_are_inert(client):
    for evil in ["' OR 1=1 --", '%', '_', '\\', '"; DROP TABLE individuals;--']:
        r = client.get('/results/2025-26/individuals/', query_string={'q': evil, 'school': evil})
        assert r.status_code == 200
    assert client.get('/results/search/', query_string={'q': "x' UNION SELECT 1--"}).status_code == 200
    assert 'Alexandra B.' in client.get('/results/2025-26/individuals/?q=Alexandra').get_data(as_text=True)


def test_search_finds_schools_and_students(client):
    html = client.get('/results/search/?q=lexington').get_data(as_text=True)
    assert 'Lexington Clarke' in html and 'Schools (' in html
    html = client.get('/results/search/?q=alexandra&season=2025-26').get_data(as_text=True)
    assert 'Alexandra B.' in html


def test_search_requires_two_characters(client):
    assert 'at least two characters' in client.get('/results/search/?q=a').get_data(as_text=True)


def test_blank_names_are_shown_as_dash_not_invented(client):
    html = client.get('/results/2015-16/individuals/').get_data(as_text=True)
    assert '>—</a>' in html


@pytest.mark.parametrize('path', [
    '/results/2025-26/individuals/', '/results/2025-26/individuals/1/', '/results/search/?q=lexington',
])
def test_student_pages_are_noindex(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    assert 'noindex' in resp.headers['X-Robots-Tag']
    assert '<meta name="robots" content="noindex, nofollow">' in resp.get_data(as_text=True)
    assert '<link rel="canonical"' not in resp.get_data(as_text=True)


def test_team_pages_remain_indexable(client):
    resp = client.get('/results/2025-26/teams/')
    assert 'X-Robots-Tag' not in resp.headers
    assert 'noindex' not in resp.get_data(as_text=True)


def test_student_detail(client):
    html = client.get('/results/2025-26/individuals/1/').get_data(as_text=True)
    assert 'Round-by-round scores' in html and 'Round 5' in html


def test_unknown_season_and_bad_ids_404(client):
    for p in ['/results/1999-00/teams/', '/results/2025-26/individuals/999999/', '/results/abc/',
              '/results/2026-27/teams/', '/contests/2026-27/dates/', '/results/school/?name=Nope+School']:
        assert client.get(p).status_code == 404, p
