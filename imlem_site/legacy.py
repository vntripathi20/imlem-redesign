"""Mapping from old imlem.org paths to their new URLs.

One pure function, ``new_url_for_old_path``, drives both the redirect routes
and the link rewriting done by the archive importer, so the two can never
disagree. It returns ``None`` for paths that have no equivalent.
"""
import re
from urllib.parse import urlparse

CONTACT_ROLES = {'president', 'tabulator', 'treasurer', 'contestwriter'}


def season_id(code):
    """'201516' -> '2015-16'."""
    return f'{code[:4]}-{code[4:]}'


def season_code(season):
    """'2015-16' -> '201516'."""
    return season.replace('-', '')


def normalize(path):
    path = urlparse(path).path or '/'
    if not path.startswith('/'):
        path = '/' + path
    if path.endswith('/index.html'):
        path = path[: -len('index.html')]
    elif path.endswith('/index.htm'):
        path = path[: -len('index.htm')]
    return path


_TOPICS = re.compile(r'^/meetinfo/(?:\d{6}/)?(\d{6})topics\.html$')
_DATES = re.compile(r'^/meetinfo/(?:\d{6}/)?(\d{6})datessites\.html$')
_CLUSTER = re.compile(r'^/meetinfo/(\d{6})/cluster/(\d{1,2}|pa)\.html$')
_CLUSTER_ALL = re.compile(r'^/meetinfo/(\d{6})/cluster/$')
_STATS = re.compile(r'^/statistics/\d{6}/(\d{6})_(individual|team_bydivision|team)\.html$')
_OFFICERS = re.compile(r'^/leagueinfo/\d{6}/(\d{6})officers\.html$')
_TOPICS_PDF = re.compile(r'^/meetinfo/\d{6}/(\d{6})topics\.pdf$')

_STATS_VIEW = {'individual': 'individuals', 'team_bydivision': 'divisions', 'team': 'teams'}

_FIXED = {
    '/': '/',
    '/meetinfo/': '/contests/',
    '/meetinfo/calculators.html': '/rules/calculators/',
    '/statistics/': '/results/',
    '/studymaterials/': '/study/',
    '/leagueinfo/': '/about/',
    '/leagueinfo/bylaws/2003bylaws.html': '/about/bylaws/',
    '/contact/': '/contact/',
    '/contact/whotocontact.html': '/contact/#who',
    '/links/': '/links/',
    '/coaches/': '/coaches/',
    '/favicon.ico': '/favicon.ico',
    '/imlem.css': '/static/css/site.css',
    '/sorttable.js': '/static/js/tables.js',
    '/logos/50th_anniversary.gif': '/static/img/50th-anniversary.gif',
}


def new_url_for_old_path(path):
    """Return the new URL for an old site path, or None if unknown."""
    path = normalize(path)
    if path in _FIXED:
        return _FIXED[path]
    if path.endswith('/favicon.ico'):
        return '/favicon.ico'
    if path.endswith('/pdf.gif'):
        return '/static/img/pdf.gif'
    m = _TOPICS.match(path)
    if m:
        return f'/contests/{season_id(m.group(1))}/topics/'
    m = _DATES.match(path)
    if m:
        return f'/contests/{season_id(m.group(1))}/dates/'
    m = _CLUSTER.match(path)
    if m:
        return f'/contests/{season_id(m.group(1))}/clusters/{m.group(2)}/'
    m = _CLUSTER_ALL.match(path)
    if m:
        return f'/contests/{season_id(m.group(1))}/clusters/'
    m = _STATS.match(path)
    if m:
        return f'/results/{season_id(m.group(1))}/{_STATS_VIEW[m.group(2)]}/'
    m = _OFFICERS.match(path)
    if m:
        return f'/about/officers/{season_id(m.group(1))}/'
    m = _TOPICS_PDF.match(path)
    if m:
        return f'/files/{m.group(1)}-round-topics.pdf'
    m = re.match(r'^/contact/(\w+)\.html$', path)
    if m and m.group(1) in CONTACT_ROLES:
        return f'/contact/{m.group(1)}/'
    return None
