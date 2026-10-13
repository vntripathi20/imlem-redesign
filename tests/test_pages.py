import re
import xml.etree.ElementTree as ET

import pytest

PAGES = [
    '/', '/about/', '/about/bylaws/', '/about/officers/', '/about/officers/2022-23/', '/join/', '/contests/',
    '/contests/2025-26/', '/contests/2026-27/topics/', '/contests/2024-25/dates/', '/contests/2024-25/clusters/',
    '/contests/2024-25/clusters/1/', '/rules/calculators/', '/results/', '/results/2025-26/',
    '/results/2025-26/teams/', '/results/2025-26/divisions/', '/results/2025-26/individuals/',
    '/results/2019-20/individuals/', '/results/search/?q=lexington', '/results/school/?name=Lexington+Clarke',
    '/study/', '/study/?topic=Geometry&meet=3', '/links/', '/contact/', '/contact/president/', '/coaches/', '/50th/',
    '/robots.txt', '/sitemap.xml', '/favicon.ico',
]


@pytest.mark.parametrize('path', PAGES)
def test_page_ok(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, path


@pytest.mark.parametrize('path', [p for p in PAGES if not p.endswith(('.txt', '.xml', '.ico'))])
def test_html_basics(client, path):
    html = client.get(path).get_data(as_text=True)
    assert '<html lang="en">' in html
    assert 'class="skip-link"' in html
    assert html.count('<h1') == 1, 'exactly one h1'
    assert re.search(r'<title>[^<]+</title>', html)
    assert 'name="description"' in html
    assert '<main id="main"' in html
    # no inline scripts/styles (CSP) and no images without alt
    assert not re.search(r'<script(?![^>]*src=)[^>]*>', html)
    assert ' style="' not in html
    for img in re.findall(r'<img\b[^>]*>', html):
        assert ' alt=' in img, img


def test_home_leads_with_season_schedule(client):
    html = client.get('/').get_data(as_text=True)
    assert 'Intermediate Math League of Eastern Massachusetts' in html
    main = html.split('<main', 1)[1]
    # the season's meet table comes before everything else on the page
    assert 'class="data schedule"' in main or 'No meet dates are published yet' in main
    assert main.count('50-years.png') <= 1


def test_home_marks_the_next_meet(app):
    from datetime import date
    from unittest import mock
    import imlem_site.web as web
    with mock.patch.object(web, 'date', wraps=date) as d:
        d.today.return_value = date(2026, 10, 12)
        html = app.test_client().get('/').get_data(as_text=True)
    assert '2026-27 season' in html
    assert 'Next meet, in 3 days' in html
    assert 'Meet 1 rounds' in html and 'subj-geometry' in html


def test_round_labels_have_no_html_entities(client):
    html = client.get('/contests/2026-27/topics/').get_data(as_text=True)
    assert '&amp;nbsp;' not in html and 'Round&nbsp;' not in html
    assert '>Round 1<' in html


def test_2025_26_meet_3_date_is_consistent(client):
    teams = client.get('/results/2025-26/teams/').get_data(as_text=True)
    indiv = client.get('/results/2025-26/individuals/').get_data(as_text=True)
    assert 'Jan. 4, 2026' not in teams
    assert 'Jan. 8, 2026' in teams and 'Jan. 8, 2026' in indiv


def test_next_meet_uses_today(app):
    from datetime import date
    from imlem_site import db as D
    with app.app_context():
        m = D.next_meet(date(2026, 10, 12))
        assert (m['season'], m['number'], m['date_iso']) == ('2026-27', 1, '2026-10-15')
        m = D.next_meet(date(2027, 2, 26))
        assert (m['number'], m['date_iso']) == (5, '2027-04-01')
        assert D.next_meet(date(2030, 1, 1)) is None


def test_topics_2026_27_content_matches_old_site(client):
    html = client.get('/contests/2026-27/topics/').get_data(as_text=True)
    for needle in ['October 15, 2026', 'February 25, 2027', 'Angle measures in plane figures',
                   'Solving quadratics with rational solutions', 'Calculator meet']:
        assert needle in html
    assert html.count('class="meet"') == 5


def test_calculator_rules_text(client):
    html = client.get('/rules/calculators/').get_data(as_text=True)
    assert 'Calculators are allowed in meets 4 and 5' in html
    assert 'Programmable or graphing calculators are NOT allowed' in html


def test_coaches_page_points_to_the_president_and_is_not_linked(client):
    html = client.get('/coaches/').get_data(as_text=True)
    assert 'Coming soon' not in html and 'noindex' in html
    assert '/contact/president/' in html
    # until the league supplies Coaches' Corner content, other pages do not link to it
    for p in ['/', '/about/', '/join/', '/contests/']:
        main_and_footer = client.get(p).get_data(as_text=True).split('<main', 1)[1]
        assert 'href="/coaches/"' not in main_and_footer, p


def test_join_page_directs_to_president_without_a_form(client):
    html = client.get('/join/').get_data(as_text=True)
    assert 'contacting the league president' in html
    assert '<form' not in html.split('<main', 1)[1].split('</main>')[0]
    assert 'Pending confirmation' not in html and 'old site' not in html


def test_contact_keeps_obfuscated_emails_and_routing_table(client):
    html = client.get('/contact/').get_data(as_text=True)
    assert 'Who should I contact?' in html
    assert 'Joining the league' in html and 'Dues' in html
    assert 'LASTNAME' in html
    assert 'mailto:' not in html and '<form' not in html.split('<main', 1)[1].split('</main>')[0]
    pres = client.get('/contact/president/').get_data(as_text=True)
    assert 'kelly_LASTNAME@wayland.k12.ma.us' in pres
    assert 'Pending confirmation' not in pres and 'old imlem.org' not in pres


def test_study_page_links_out_and_says_so(client):
    html = client.get('/study/').get_data(as_text=True)
    assert 'hosted externally' in html
    assert 'matharchive.org/imlem/2025-26/202510_imlem.pdf' in html
    assert 'prepforstem.com' in html
    # no PDFs are mirrored locally except files the league hosts itself
    assert 'href="/files/' not in html or '201516' in html


def test_study_topic_filter(client):
    html = client.get('/study/?topic=Geometry&season=2026-27').get_data(as_text=True)
    assert 'Angle measures in plane figures' in html
    assert 'Divisibility rules' not in html


def test_404_page_is_helpful(client):
    resp = client.get('/no/such/page/')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 404
    assert 'couldn' in html and 'Search schools and students' in html
    assert 'noindex' in html


def test_sitemap_is_valid_and_excludes_student_pages(client):
    resp = client.get('/sitemap.xml')
    root = ET.fromstring(resp.data)
    locs = [e.text for e in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(locs) > 150
    assert 'https://example.test/results/2025-26/teams/' in locs
    assert not any('/individuals/' in l or '/search/' in l for l in locs), 'student names must stay out of the sitemap'
    assert all(l.startswith('https://example.test/') for l in locs)


def test_robots(client):
    body = client.get('/robots.txt').get_data(as_text=True)
    assert 'Sitemap: https://example.test/sitemap.xml' in body


def test_no_founding_year_is_invented(client):
    for p in ['/', '/50th/']:
        assert '1974' not in client.get(p).get_data(as_text=True)


def test_pages_read_as_finished(client):
    """No visible references to the old site, placeholders or pending notes (TODOs live in comments and docs)."""
    import html as _html
    import re as _re
    bad = _re.compile(r"old site|old imlem|original imlem|previous imlem|carried over|pending confirmation|"
                      r"coming soon|placeholder|being rebuilt|re-checked|TODO", _re.I)
    pages = ['/', '/about/', '/about/bylaws/', '/about/officers/', '/about/officers/2022-23/', '/join/', '/50th/',
             '/coaches/', '/contests/', '/contests/2026-27/', '/contests/2026-27/topics/', '/results/',
             '/results/2025-26/', '/results/2025-26/individuals/', '/study/', '/links/', '/contact/',
             '/contact/president/', '/contact/who/', '/nope']
    for p in pages:
        body = client.get(p).get_data(as_text=True)
        body = _re.sub(r'<!--.*?-->', ' ', body, flags=_re.S)
        body = _re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=_re.S)
        text = _html.unescape(_re.sub(r'<[^>]+>', ' ', body))
        found = bad.search(text)
        assert not found, f'{p}: ...{text[max(0, found.start() - 40):found.end() + 40]}...'
