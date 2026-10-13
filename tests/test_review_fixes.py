"""Regression tests for the design/bug review: entity leaks, meet dates, pinned columns, restrained home page."""
import re
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parent.parent / 'docs' / 'pending-league-decisions.md'

PAGES = ['/', '/contests/2026-27/topics/', '/contests/2025-26/topics/', '/contests/2015-16/topics/',
         '/results/2025-26/teams/', '/results/2025-26/divisions/', '/results/2025-26/individuals/',
         '/study/', '/study/?topic=Geometry', '/contests/2025-26/', '/contact/', '/about/bylaws/']


@pytest.mark.parametrize('path', PAGES)
def test_no_literal_or_double_escaped_entities(client, path):
    html = client.get(path).get_data(as_text=True)
    for bad in ('&amp;nbsp;', '&amp;amp;', '&amp;#', '&amp;lt;', '&nbsp;Round'):
        assert bad not in html, (path, bad)
    assert not re.search(r'&amp;[a-z]+;', html), (path, re.findall(r'&amp;[a-z]+;', html)[:3])


def test_round_labels_render_as_plain_text(client):
    html = client.get('/contests/2026-27/topics/').get_data(as_text=True)
    assert len(re.findall(r'<th scope="row"[^>]*>Round [1-5]</th>', html)) == 25
    assert re.search(r'<th scope="row"[^>]*>Team Round</th>', html)


def test_database_has_no_entities_in_text(app):
    import sqlite3
    db = sqlite3.connect(app.config['DB_PATH'])
    for tbl, col in [('rounds', 'label'), ('rounds', 'category'), ('rounds', 'description'), ('meets', 'heading')]:
        n = db.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {col} LIKE '%&%;%'").fetchone()[0]
        assert n == 0, (tbl, col)


# The archive's own pages disagree on four meet dates (see docs/pending-league-decisions.md).
# Every page shows the date from the season's published schedule (the Round Topics page).
@pytest.mark.parametrize('season,meet,right,wrong', [
    ('2025-26', 3, 'Jan. 8, 2026', 'Jan. 4, 2026'),
    ('2018-19', 1, 'Oct. 25, 2018', 'Oct. 15, 2018'),
    ('2022-23', 2, 'Dec. 8, 2022', 'Dec. 2, 2022'),
    ('2024-25', 5, 'Apr. 3, 2025', 'Apr. 4, 2025'),
])
def test_one_date_per_meet_on_every_page(client, season, meet, right, wrong):
    for view in ('teams', 'divisions', 'individuals'):
        html = client.get(f'/results/{season}/{view}/').get_data(as_text=True)
        assert right in html, (season, view)
        assert wrong not in html, (season, view)


def test_date_disagreements_are_documented():
    text = DOCS.read_text(encoding='utf-8')
    for needle in ['2025-26', 'Jan. 4', 'Jan. 8', '2018-19', 'Oct. 15', '2022-23', 'Dec. 2', '2024-25', 'Apr. 4']:
        assert needle in text, needle


def test_wide_tables_pin_rank_and_name_first(client):
    ind = client.get('/results/2025-26/individuals/').get_data(as_text=True)
    heads = re.findall(r'<th scope="col"[^>]*>', ind)
    assert 'c-rank' in heads[0] and 'c-name' in heads[1]
    row = re.search(r'<tbody>\s*<tr>(.*?)</tr>', ind, re.S).group(1)
    assert row.lstrip().startswith('<td class="c-rank"')
    assert '<th scope="row" class="c-name"' in row
    assert 'table-wide' in ind and 'role="region"' in ind and 'tabindex="0"' in ind
    teams = client.get('/results/2025-26/teams/').get_data(as_text=True)
    th = re.findall(r'<th scope="col"[^>]*>', teams)
    assert 'c-rank' in th[0] and 'c-name' in th[1] and 'table-wide' in teams


def test_css_pins_columns_and_keeps_tabs_on_one_row():
    css = (Path(__file__).resolve().parent.parent / 'static' / 'css' / 'site.css').read_text(encoding='utf-8')
    assert re.search(r'\.table-wide \.c-rank[^{]*\{[^}]*position: sticky', css)
    assert re.search(r'\.tabs \{[^}]*flex-wrap: nowrap[^}]*overflow-x: auto', css)
    assert 'nth-child(4)' not in css, 'pinning must follow the c-rank/c-name classes, not a column position'
    assert 'border-radius: 999px' not in css and 'border-radius: 99' not in css, 'no pill buttons'


def test_home_is_a_season_table_not_a_hero(client, app):
    from imlem_site import db as D
    html = client.get('/').get_data(as_text=True)
    assert 'class="hero' not in html and 'eyebrow' not in html
    assert 'btn-primary' not in html and 'btn-ghost' not in html and 'nav-cta' not in html, 'no pill / gold buttons'
    assert 'class="cards' not in html and 'stats-row' not in html and 'next-count' not in html
    assert len(re.findall(r'<img[^>]*50-years', html)) == 1, 'anniversary graphic appears once'
    body = html.split('<main', 1)[1]
    assert body.index('class="data schedule"') < body.index('Announcements'), 'the schedule leads the page'
    assert len(re.findall(r'<tr[^>]*>\s*<th scope="row">\d</th>', body)) == 5, 'five meets in the season table'
    with app.app_context():
        nxt = D.next_meet()
    assert len(re.findall(r'class="is-next"', html)) == (1 if nxt else 0)


def test_join_is_a_plain_nav_link(client):
    html = client.get('/').get_data(as_text=True)
    assert re.search(r'<li><a href="/join/">Join</a></li>', html)


def test_contact_roles_are_a_table_not_cards(client):
    html = client.get('/contact/').get_data(as_text=True)
    assert 'class="card' not in html and 'class="notice' not in html
    main = html.split('<main', 1)[1]
    assert main.count('<table class="data roles"') == 1
    assert 'Pending confirmation by the league' in main


def test_yellow_notice_style_is_gone_from_pages(client):
    for p in ['/', '/join/', '/contact/', '/study/', '/links/', '/about/officers/', '/coaches/', '/50th/']:
        assert 'class="notice"' not in client.get(p).get_data(as_text=True), p


def test_footer_has_no_anniversary_graphic(client):
    html = client.get('/contests/').get_data(as_text=True)
    assert '50-years.png' not in html.split('<footer', 1)[1]
