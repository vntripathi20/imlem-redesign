"""Every URL the old site served (from the crawl) must redirect somewhere that works."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import pytest

ARCHIVE = Path(__file__).resolve().parent.parent / 'archive'
META = json.loads((ARCHIVE / 'meta.json').read_text())
ERRORS = json.loads((ARCHIVE / 'errors.json').read_text())
# Everything the crawl fetched, plus the URLs that errored on the old site itself
# (the Coaches' Corner 401 and a handful of dead links).
OLD_PATHS = sorted({urlparse(u).path or '/' for u in list(META) + list(ERRORS)})


def test_crawl_is_present():
    assert len(OLD_PATHS) >= 250


@pytest.mark.parametrize('path', OLD_PATHS)
def test_old_url_resolves(client, path):
    resp = client.get(path)
    if path in ('/', '/favicon.ico'):       # served directly, same URL
        assert resp.status_code == 200
        return
    assert resp.status_code == 301, f'{path} -> {resp.status_code}'
    target = resp.headers['Location']
    assert target.startswith('/') and not target.startswith('//'), target
    final = client.get(target)
    assert final.status_code == 200, f'{path} -> {target} -> {final.status_code}'


@pytest.mark.parametrize('path,expected', [
    ('/statistics/202526/202526_individual.html', '/results/2025-26/individuals/'),
    ('/statistics/202526/202526_team_bydivision.html', '/results/2025-26/divisions/'),
    ('/statistics/202526/202526_team.html', '/results/2025-26/teams/'),
    ('/meetinfo/202627/202627topics.html', '/contests/2026-27/topics/'),
    ('/meetinfo/202425/202425datessites.html', '/contests/2024-25/dates/'),
    ('/meetinfo/202425/cluster/1.html', '/contests/2024-25/clusters/1/'),
    ('/meetinfo/calculators.html', '/rules/calculators/'),
    ('/leagueinfo/bylaws/2003bylaws.html', '/about/bylaws/'),
    ('/contact/whotocontact.html', '/contact/#who'),
    ('/statistics/index.html', '/results/'),
    ('/studymaterials/index.html', '/study/'),
    ('/index.html', '/'),
    # the old site's own dead links point at the right season's page
    ('/meetinfo/202425/201819topics.html', '/contests/2018-19/topics/'),
])
def test_known_mappings(client, path, expected):
    resp = client.get(path)
    assert resp.status_code in (301, 200)
    if path != '/index.html' or resp.status_code == 301:
        assert resp.headers['Location'] == expected


def test_www_host_and_trailing_variants(client):
    assert client.get('/statistics/').status_code == 301
    assert client.get('/meetinfo/').headers['Location'] == '/contests/'


def test_rewritten_links_inside_pages_all_resolve(client):
    """Links inside migrated old pages must point at pages that exist."""
    bad = []
    for page in ['/contests/2024-25/dates/', '/contests/2024-25/clusters/1/', '/about/officers/2022-23/',
                 '/links/', '/contact/', '/about/bylaws/', '/contests/2019-20/clusters/']:
        html = client.get(page).get_data(as_text=True)
        for href in re.findall(r'href="(/[^"#]*)', html):
            if href.startswith(('/static/', '/images/')):
                continue
            if client.get(href).status_code != 200:
                bad.append((page, href))
    assert not bad, bad[:10]


def test_stale_link_on_2024_25_dates_page_is_fixed(client):
    html = client.get('/contests/2024-25/dates/').get_data(as_text=True)
    assert '/contests/2018-19/topics/' not in html
    assert '/contests/2024-25/topics/#1' in html
