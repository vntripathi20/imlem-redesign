"""Flask application factory: server-rendered pages with real URLs."""
import json
import math
import os
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

from flask import (Flask, abort, g, make_response, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix

from . import config as cfg
from . import db as D
from .legacy import new_url_for_old_path, season_code

SEASON_RE = re.compile(r'^\d{4}-\d{2}$')
NOINDEX = 'noindex, nofollow'

INDIVIDUAL_SORTS = {
    'rank': 'overall_rank_n', 'name': 'name_lc', 'school': 'school_lc', 'grade': 'grade',
    'division': 'division', 'total': 'total', 'total5': 'total5',
}


def create_app(test_config=None):
    app = Flask(__name__, static_folder=str(cfg.BASE_DIR / 'static'), template_folder=str(cfg.BASE_DIR / 'templates'))
    debug = cfg.env_flag('FLASK_DEBUG')
    app.config.update(
        DEBUG=debug,
        DB_PATH=Path(os.environ.get('IMLEM_DB') or cfg.DATA_DIR / 'imlem.sqlite'),
        ARCHIVE_DIR=cfg.ARCHIVE_DIR,
        SITE_URL=os.environ.get('IMLEM_SITE_URL', '').rstrip('/'),
        MAX_CONTENT_LENGTH=64 * 1024,  # the site accepts no uploads or form bodies
        SESSION_COOKIE_SECURE=not debug,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        # Only needed if a feature that uses sessions is ever added; there are none today.
        SECRET_KEY=os.environ.get('IMLEM_SECRET_KEY') or os.urandom(32),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    if cfg.env_flag('IMLEM_TRUST_PROXY'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    D.ensure_database(app)
    app.teardown_appcontext(D.close_db)
    register_filters(app)
    register_hooks(app)
    register_routes(app)
    register_errors(app)
    return app


# --------------------------------------------------------------------------- helpers

def site_url(path=''):
    base = g.get('site_base') or ''
    return base + path


def render(template, *, title, description='', crumbs=None, robots=None, **ctx):
    crumbs = [('Home', url_for('home'))] + (crumbs or [])
    g.robots = robots
    return render_template(
        template, title=title, description=description or cfg.SITE_FULL_NAME, crumbs=crumbs,
        robots=robots, canonical=site_url(request.path), **ctx,
    )


def valid_season(season):
    if not SEASON_RE.match(season) or not D.q1('SELECT 1 FROM seasons WHERE id=?', season):
        abort(404)
    return season


def load_json(name, default):
    path = cfg.DATA_DIR / name
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def page_or_404(kind, key):
    row = D.page(kind, key)
    if not row:
        abort(404)
    return row


def human_date(iso):
    d = datetime.strptime(iso, '%Y-%m-%d').date()
    return f'{d.strftime("%A, %B")} {d.day}, {d.year}'


# --------------------------------------------------------------------------- filters/hooks

def register_filters(app):
    @app.template_filter('subject')
    def subject_class(category):
        return 'subj-' + re.sub(r'[^a-z]+', '-', (category or '').lower()).strip('-')

    @app.template_filter('score')
    def score(v):
        return '' if v is None else v

    @app.template_filter('name_or_dash')
    def name_or_dash(v):
        return v if v else '—'

    @app.context_processor
    def inject():
        return {
            'site_name': cfg.SITE_NAME, 'site_full_name': cfg.SITE_FULL_NAME,
            'officers_last_confirmed': cfg.OFFICERS_LAST_CONFIRMED,
            'nav': [
                ('Contests', url_for('contests'), 'contests'),
                ('Results', url_for('results'), 'results'),
                ('Study materials', url_for('study'), 'study'),
                ('About', url_for('about'), 'about'),
                ('Join', url_for('join'), 'join'),
                ('Contact', url_for('contact'), 'contact'),
            ],
            'current_year': date.today().year,
        }


def register_hooks(app):
    @app.before_request
    def base_url():
        g.site_base = app.config['SITE_URL'] or request.url_root.rstrip('/')

    @app.before_request
    def legacy_redirect():
        """Old imlem.org URLs 301 to their new home. Runs before routing so that e.g.
        /contact/president.html is not mistaken for the new /contact/<role>/ route."""
        path = request.path
        if path.startswith(('/static/', '/files/', '/images/', '/uploads/')):
            return None
        new = new_url_for_old_path(path)
        if new and new != path:
            return redirect(new, 301)
        return None

    @app.after_request
    def headers(resp):
        resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
        resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        resp.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        resp.headers.setdefault('X-Frame-Options', 'DENY')
        resp.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'",
        )
        if not app.config['DEBUG'] and request.is_secure:
            resp.headers.setdefault('Strict-Transport-Security', 'max-age=31536000')
        if g.get('robots'):
            resp.headers['X-Robots-Tag'] = g.robots
        if request.path.startswith('/static/') and 'Cache-Control' not in resp.headers:
            resp.headers['Cache-Control'] = 'public, max-age=86400'
        return resp


# --------------------------------------------------------------------------- routes

def register_routes(app):
    # ---- home -----------------------------------------------------------------
    @app.route('/')
    def home():
        today = date.today()
        nxt = D.next_meet(today)
        # Show the season of the next meet; after the last meet of a season, the most recent season.
        season = nxt['season'] if nxt else (D.seasons() or [None])[0]
        meets = D.meets_for(season) if season else []
        rounds = {}
        for r in D.q('SELECT * FROM rounds WHERE season=? ORDER BY meet, seq', season):
            rounds.setdefault(r['meet'], []).append(r)
        days_to_next = (date.fromisoformat(nxt['date_iso']) - today).days if nxt else None
        res = D.results_seasons()
        top_teams = []
        if res:
            top_teams = D.q("SELECT * FROM teams WHERE season=? AND scope='overall' ORDER BY seq LIMIT 5", res[0])
        announcements = [a for a in load_json('announcements.json', {}).get('items', []) if a.get('title')]
        return render('home.html', title=f'{cfg.SITE_NAME} — {cfg.SITE_FULL_NAME}',
                      description='IMLEM is a middle school math league in Eastern Massachusetts. '
                                  'Meet dates, round topics, a results archive and study materials.',
                      season=season, meets=meets, rounds=rounds, nxt=nxt, days_to_next=days_to_next,
                      human_date=human_date, latest_season=res[0] if res else None,
                      earliest_season=res[-1] if res else None, top_teams=top_teams,
                      announcements=announcements, home=True)

    # ---- about / join / rules -------------------------------------------------
    @app.route('/about/')
    def about():
        officer_seasons = [r['key'] for r in D.q("SELECT key FROM pages WHERE kind='officers' ORDER BY key DESC")]
        return render('about.html', title='About the League',
                      description='About IMLEM: league information, officers, and the League Bylaws.',
                      crumbs=[('About', None)], officer_seasons=officer_seasons)

    @app.route('/about/bylaws/')
    def bylaws():
        p = page_or_404('bylaws', '2003')
        return render('content.html', title='League Bylaws (2003)',
                      description='The IMLEM League Bylaws, last updated 2003: team make-up, test description, '
                                  'meet procedures, officers and awards.',
                      crumbs=[('About', url_for('about')), ('Bylaws', None)], page=p, heading='League Bylaws',
                      notice='The Bylaws were last updated in 2003, as stated on the old site.', wide=True)

    @app.route('/about/officers/')
    def officers_index():
        keys = [r['key'] for r in D.q("SELECT key FROM pages WHERE kind='officers' ORDER BY key DESC")]
        return render('officers_index.html', title='League officers by season',
                      crumbs=[('About', url_for('about')), ('Officers', None)], keys=keys)

    @app.route('/about/officers/<season>/')
    def officers(season):
        valid_season(season)
        p = page_or_404('officers', season)
        keys = [r['key'] for r in D.q("SELECT key FROM pages WHERE kind='officers' ORDER BY key DESC")]
        older, newer = D.neighbours(season, keys)
        return render('content.html', title=f'League officers {season}',
                      crumbs=[('About', url_for('about')), ('Officers', url_for('officers_index')), (season, None)],
                      page=p, heading=f'League Officers and Cluster Coordinators, {season}',
                      prev=(older, url_for('officers', season=older) if older else None),
                      next=(newer, url_for('officers', season=newer) if newer else None),
                      pending_note=season == cfg.OFFICERS_LAST_CONFIRMED,
                      notice=(f'The most recent officer list the old site published is {cfg.OFFICERS_LAST_CONFIRMED}. '
                              'Current officers are not yet confirmed.'
                              if season == cfg.OFFICERS_LAST_CONFIRMED else None))

    @app.route('/join/')
    def join():
        president = D.page('contact', 'president')
        return render('join.html', title='How to join the league',
                      description='How a school joins IMLEM: contact the league president.',
                      crumbs=[('Join', None)], president=president)

    @app.route('/rules/calculators/')
    def calculators():
        p = page_or_404('calculators', 'calculators')
        return render('content.html', title='Calculator rules',
                      description='IMLEM calculator policy: allowed in meets 4 and 5; no programmable or graphing calculators.',
                      crumbs=[('Contests', url_for('contests')), ('Calculator rules', None)],
                      page=p, heading='Calculator Rules')

    @app.route('/50th/')
    def anniversary():
        return render('anniversary.html', title='IMLEM at 50',
                      description='IMLEM — 50 years and still counting.',
                      crumbs=[('About', url_for('about')), ('50th anniversary', None)])

    @app.route('/coaches/')
    def coaches():
        return render('coaches.html', title="Coaches' Corner (coming soon)",
                      crumbs=[("Coaches' Corner", None)], robots=NOINDEX)

    # ---- contests -------------------------------------------------------------
    @app.route('/contests/')
    def contests():
        rows = [D.season_summary(s) for s in D.seasons()]
        return render('contests.html', title='Contests: dates, sites and round topics',
                      description='IMLEM meet dates and sites, round topics, clusters and calculator rules, by season.',
                      crumbs=[('Contests', None)], rows=rows)

    @app.route('/contests/<season>/')
    def season_hub(season):
        valid_season(season)
        summary = D.season_summary(season)
        seasons = D.seasons()
        older, newer = D.neighbours(season, seasons)
        return render('season.html', title=f'{season} season',
                      description=f'IMLEM {season}: round topics, dates and sites, clusters and results.',
                      crumbs=[('Contests', url_for('contests')), (season, None)], s=summary, meets=D.meets_for(season),
                      prev=(older, url_for('season_hub', season=older) if older else None),
                      next=(newer, url_for('season_hub', season=newer) if newer else None))

    @app.route('/contests/<season>/topics/')
    def topics(season):
        valid_season(season)
        meets = D.meets_for(season)
        if not meets:
            abort(404)
        rounds = {}
        for r in D.q('SELECT * FROM rounds WHERE season=? ORDER BY meet, seq', season):
            rounds.setdefault(r['meet'], []).append(r)
        have = [r['season'] for r in D.q('SELECT DISTINCT season FROM meets ORDER BY season DESC')]
        older, newer = D.neighbours(season, have)
        return render('topics.html', title=f'Round topics {season}',
                      description=f'IMLEM round topics for the {season} season, meet by meet.',
                      crumbs=[('Contests', url_for('contests')), (season, url_for('season_hub', season=season)), ('Round topics', None)],
                      season=season, meets=meets, rounds=rounds,
                      prev=(older, url_for('topics', season=older) if older else None),
                      next=(newer, url_for('topics', season=newer) if newer else None))

    @app.route('/contests/<season>/dates/')
    def dates(season):
        valid_season(season)
        p = page_or_404('dates', season)
        keys = [r['key'] for r in D.q("SELECT key FROM pages WHERE kind='dates' ORDER BY key DESC")]
        older, newer = D.neighbours(season, keys)
        return render('content.html', title=f'Dates and sites {season}',
                      description=f'IMLEM meet dates and host sites for {season}.',
                      crumbs=[('Contests', url_for('contests')), (season, url_for('season_hub', season=season)), ('Dates and sites', None)],
                      page=p, heading=f'Dates and Sites {season}', wide=True,
                      prev=(older, url_for('dates', season=older) if older else None),
                      next=(newer, url_for('dates', season=newer) if newer else None))

    @app.route('/contests/<season>/clusters/')
    def clusters(season):
        valid_season(season)
        p = page_or_404('clusters', season)
        return render('content.html', title=f'Clusters {season}',
                      description=f'IMLEM geographic clusters and member schools, {season}.',
                      crumbs=[('Contests', url_for('contests')), (season, url_for('season_hub', season=season)), ('Clusters', None)],
                      page=p, heading=f'Clusters {season}', wide=True)

    @app.route('/contests/<season>/clusters/<cluster>/')
    def cluster(season, cluster):
        valid_season(season)
        if not re.fullmatch(r'\d{1,2}|pa', cluster):
            abort(404)
        p = page_or_404('cluster', f'{season}/{cluster}')
        # Some seasons (e.g. 2020-21) have cluster pages but no all-clusters index page.
        index_url = url_for('clusters', season=season) if D.page('clusters', season) else None
        return render('content.html', title=f'{season} Cluster {cluster.upper() if cluster == "pa" else cluster}',
                      crumbs=[('Contests', url_for('contests')), (season, url_for('season_hub', season=season)),
                              ('Clusters', index_url), (cluster, None)],
                      page=p, heading=p['title'])

    # ---- results --------------------------------------------------------------
    @app.route('/results/')
    def results():
        rows = []
        for s in D.results_seasons():
            n_ind = D.q1('SELECT COUNT(*) AS n FROM individuals WHERE season=?', s)['n']
            n_team = D.q1("SELECT COUNT(*) AS n FROM teams WHERE season=? AND scope='overall'", s)['n']
            rows.append({'season': s, 'individuals': n_ind, 'teams': n_team, 'divisions': len(D.season_divisions(s))})
        return render('results.html', title='Results archive',
                      description='IMLEM results for every archived season: team rankings overall and by division, '
                                  'and individual rankings. Search by school or student.',
                      crumbs=[('Results', None)], rows=rows)

    @app.route('/results/<season>/')
    def results_season(season):
        valid_season(season)
        if not D.q1('SELECT 1 FROM individuals WHERE season=?', season):
            abort(404)
        res = D.results_seasons()
        older, newer = D.neighbours(season, res)
        return render('results_season.html', title=f'{season} results',
                      description=f'IMLEM {season} team and individual results.',
                      crumbs=[('Results', url_for('results')), (season, None)], season=season,
                      divisions=D.season_divisions(season),
                      prev=(older, url_for('results_season', season=older) if older else None),
                      next=(newer, url_for('results_season', season=newer) if newer else None))

    def team_table(season, scope):
        out = []
        for r in D.q('SELECT * FROM teams WHERE season=? AND scope=? ORDER BY seq', season, scope):
            out.append(D.decode_json_columns(r, 'scores'))
        return out

    @app.route('/results/<season>/teams/')
    def results_teams(season):
        valid_season(season)
        rows = team_table(season, 'overall')
        if not rows:
            abort(404)
        return render('results_teams.html', title=f'{season} team rankings (overall)',
                      description=f'IMLEM {season} overall team rankings by school.',
                      crumbs=[('Results', url_for('results')), (season, url_for('results_season', season=season)), ('Teams', None)],
                      season=season, rows=rows, labels=D.meet_labels(season, 'team'), n_meets=len(rows[0]['scores']))

    @app.route('/results/<season>/divisions/')
    def results_divisions(season):
        valid_season(season)
        divs = D.season_divisions(season)
        if not divs:
            abort(404)
        tables = []
        for d in divs:
            rows = team_table(season, d)
            tables.append({'name': d, 'id': re.sub(r'[^a-z0-9]+', '-', d.lower()).strip('-'), 'rows': rows})
        n = max((len(t['rows'][0]['scores']) for t in tables if t['rows']), default=5)
        return render('results_divisions.html', title=f'{season} team rankings by division',
                      description=f'IMLEM {season} team rankings within each division.',
                      crumbs=[('Results', url_for('results')), (season, url_for('results_season', season=season)), ('Divisions', None)],
                      season=season, tables=tables, labels=D.meet_labels(season, 'team'), n_meets=n,
                      code_ids={t['name']: t['id'] for t in tables})

    @app.route('/results/<season>/individuals/')
    def results_individuals(season):
        valid_season(season)
        if not D.q1('SELECT 1 FROM individuals WHERE season=?', season):
            abort(404)
        args = request.args
        where, params = ['season=?'], [season]
        name_q, school_q = args.get('q', '').strip()[:60], args.get('school', '').strip()[:80]
        division, grade = args.get('division', '').strip()[:40], args.get('grade', '').strip()[:6]
        if name_q:
            where.append("name_lc LIKE ? ESCAPE '\\'")
            params.append(D.like(name_q.lower()))
        if school_q:
            where.append("school_lc LIKE ? ESCAPE '\\'")
            params.append(D.like(school_q.lower()))
        if division:
            where.append('division=?')
            params.append(division)
        if grade:
            where.append('grade=?')
            params.append(grade)
        sort = args.get('sort', 'rank')
        sort = sort if sort in INDIVIDUAL_SORTS else 'rank'
        direction = 'DESC' if (args.get('dir') == 'desc') else 'ASC'
        order = f'{INDIVIDUAL_SORTS[sort]} {direction}, seq ASC'
        clause = ' AND '.join(where)
        total = D.q1(f'SELECT COUNT(*) AS n FROM individuals WHERE {clause}', *params)['n']
        pages = max(1, math.ceil(total / cfg.INDIVIDUALS_PER_PAGE))
        try:
            pg = min(max(1, int(args.get('page', 1))), pages)
        except ValueError:
            pg = 1
        rows = [D.decode_json_columns(r, 'meet_totals') for r in D.q(
            f'SELECT * FROM individuals WHERE {clause} ORDER BY {order} LIMIT ? OFFSET ?', *params,
            cfg.INDIVIDUALS_PER_PAGE, (pg - 1) * cfg.INDIVIDUALS_PER_PAGE)]
        divisions = [r['division'] for r in D.q(
            'SELECT division FROM individuals WHERE season=? GROUP BY division ORDER BY MIN(seq)', season)]
        grades = [r['grade'] for r in D.q('SELECT DISTINCT grade FROM individuals WHERE season=? ORDER BY grade', season)]
        labels = D.meet_labels(season, 'individual')
        # Column count comes from the data (2019-20 has four meets), not from the label dict.
        sample = D.q1('SELECT meet_totals FROM individuals WHERE season=? LIMIT 1', season)
        n_meets = len(json.loads(sample['meet_totals']))
        base = {k: v for k, v in args.items() if k != 'page'}
        return render('results_individuals.html', title=f'{season} individual rankings',
                      description=f'IMLEM {season} individual rankings.',
                      crumbs=[('Results', url_for('results')), (season, url_for('results_season', season=season)), ('Individuals', None)],
                      robots=NOINDEX, season=season, rows=rows, total=total, page_no=pg, pages=pages, labels=labels,
                      n_meets=n_meets, divisions=divisions, grades=grades, base=base,
                      page_url=lambda n: url_for('results_individuals', season=season, **dict(base, page=n)),
                      sort_url=lambda col, d: url_for('results_individuals', season=season, **dict(base, sort=col, dir=d)),
                      f={'q': name_q, 'school': school_q, 'division': division, 'grade': grade, 'sort': sort,
                         'dir': 'desc' if direction == 'DESC' else 'asc'})

    @app.route('/results/<season>/individuals/<int:seq>/')
    def student(season, seq):
        valid_season(season)
        r = D.q1('SELECT * FROM individuals WHERE season=? AND seq=?', season, seq)
        if not r:
            abort(404)
        r = D.decode_json_columns(r, 'rounds', 'meet_totals')
        return render('student.html', title=f'{r["name"] or "Unlisted student"}, {season}',
                      crumbs=[('Results', url_for('results')), (season, url_for('results_season', season=season)),
                              ('Individuals', url_for('results_individuals', season=season)), (f'#{r["overall_rank"]}', None)],
                      robots=NOINDEX, r=r, season=season, labels=D.meet_labels(season, 'individual'))

    @app.route('/results/search/')
    def search():
        term = request.args.get('q', '').strip()[:60]
        season = request.args.get('season', '').strip()
        schools, students = [], []
        if len(term) >= 2:
            pat = D.like(term.lower())
            schools = D.q("SELECT school, COUNT(DISTINCT season) AS seasons, MAX(season) AS latest FROM teams "
                          "WHERE scope='overall' AND school_lc LIKE ? ESCAPE '\\' GROUP BY school ORDER BY school LIMIT 60", pat)
            sql = "SELECT * FROM individuals WHERE name<>'' AND name_lc LIKE ? ESCAPE '\\'"
            args = [pat]
            if SEASON_RE.match(season):
                sql += ' AND season=?'
                args.append(season)
            students = D.q(sql + ' ORDER BY season DESC, overall_rank_n, seq LIMIT 200', *args)
        return render('search.html', title=f'Search results for “{term}”' if term else 'Search the results archive',
                      crumbs=[('Results', url_for('results')), ('Search', None)], robots=NOINDEX,
                      term=term, season=season, schools=schools, students=students, seasons=D.results_seasons(),
                      too_short=bool(term) and len(term) < 2)

    @app.route('/results/school/')
    def school():
        name = request.args.get('name', '').strip()[:100]
        rows = D.q("SELECT * FROM teams WHERE scope='overall' AND school=? ORDER BY season DESC", name) if name else []
        if not rows:
            abort(404)
        return render('school.html', title=f'{name}: team results by season',
                      description=f'{name} team rankings in the IMLEM results archive.',
                      crumbs=[('Results', url_for('results')), (name, None)], name=name,
                      rows=[D.decode_json_columns(r, 'scores') for r in rows])

    # ---- study ----------------------------------------------------------------
    @app.route('/study/')
    def study():
        args = request.args
        season, meet = args.get('season', '').strip(), args.get('meet', '').strip()
        cat, term = args.get('topic', '').strip()[:40], args.get('q', '').strip()[:60]
        where, params = ["r.label LIKE 'Round%'", ], []
        if SEASON_RE.match(season):
            where.append('r.season=?')
            params.append(season)
        if meet in {'1', '2', '3', '4', '5'}:
            where.append('r.meet=?')
            params.append(int(meet))
        if cat:
            where.append('r.category=?')
            params.append(cat)
        if term:
            where.append("(r.description LIKE ? ESCAPE '\\' OR r.category LIKE ? ESCAPE '\\')")
            params += [D.like(term), D.like(term)]
        clause = ' AND '.join(where)
        total = D.q1(f'SELECT COUNT(*) AS n FROM rounds r WHERE {clause}', *params)['n']
        try:
            pg = max(1, int(args.get('page', 1)))
        except ValueError:
            pg = 1
        per = 60
        pages = max(1, math.ceil(total / per))
        pg = min(pg, pages)
        rows = D.q(f'SELECT r.*, m.contest_url, m.date_text FROM rounds r JOIN meets m ON m.season=r.season AND m.number=r.meet '
                   f'WHERE {clause} ORDER BY r.season DESC, r.meet, r.seq LIMIT ? OFFSET ?', *params, per, (pg - 1) * per)
        cats = [r['category'] for r in D.q("SELECT category, COUNT(*) AS n FROM rounds WHERE label LIKE 'Round%' "
                                           "GROUP BY category HAVING n >= 5 ORDER BY category")]
        contest_seasons = []
        for s in [r['season'] for r in D.q('SELECT DISTINCT season FROM meets ORDER BY season DESC')]:
            contest_seasons.append({'season': s, 'meets': D.meets_for(s)})
        res = load_json('resources.json', {'sections': []})
        hosted = load_json('study-materials.json', {'years': []})
        base = {k: v for k, v in args.items() if k != 'page'}
        return render('study.html', title='Study materials',
                      description='Past IMLEM contests by season and meet, round topics by subject, books, videos and '
                                  'practice resources.',
                      crumbs=[('Study Materials', None)], rows=rows, total=total, page_no=pg, pages=pages, base=base,
                      page_url=lambda n: url_for('study', **dict(base, page=n)) + '#topics',
                      cats=cats, all_seasons=[r['season'] for r in D.q('SELECT DISTINCT season FROM meets ORDER BY season DESC')],
                      contest_seasons=contest_seasons, resources=res['sections'], hosted=hosted['years'],
                      f={'season': season, 'meet': meet, 'topic': cat, 'q': term},
                      archive_host=cfg.CONTEST_ARCHIVE_HOST)

    # ---- links / contact ------------------------------------------------------
    @app.route('/links/')
    def links():
        p = page_or_404('links', 'links')
        return render('content.html', title='Links to other sites',
                      description='Math leagues, competitions, enrichment programs and summer camps.',
                      crumbs=[('Links', None)], page=p, heading='Links to Other Sites',
                      notice='These links were carried over from the old site and have not all been re-checked.')

    @app.route('/contact/')
    def contact():
        who = page_or_404('who', 'who')
        return render('contact.html', title='Contact',
                      description='Who to contact at IMLEM for joining, policies, statistics, dues and contest questions.',
                      crumbs=[('Contact', None)], who=who)

    @app.route('/contact/who/')
    def contact_who():
        return redirect(url_for('contact') + '#who', 301)

    @app.route('/contact/<role>/')
    def contact_role(role):
        if role not in ('president', 'tabulator', 'treasurer', 'contestwriter'):
            abort(404)
        p = page_or_404('contact', role)
        return render('content.html', title=p['title'], crumbs=[('Contact', url_for('contact')), (p['title'], None)],
                      page=p, heading=p['title'], contact_notice=True)

    # ---- files ----------------------------------------------------------------
    @app.route('/files/<path:name>')
    def files(name):
        return send_from_directory(cfg.FILES_DIR, name)

    @app.route('/uploads/<path:name>')
    def uploads(name):
        return send_from_directory(cfg.UPLOAD_DIR, name)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(cfg.BASE_DIR / 'images', 'logo.png', mimetype='image/png')

    @app.route('/images/<path:name>')
    def images(name):
        return send_from_directory(cfg.BASE_DIR / 'images', name)

    # ---- SEO ------------------------------------------------------------------
    @app.route('/robots.txt')
    def robots():
        body = f'User-agent: *\nAllow: /\nSitemap: {site_url("/sitemap.xml")}\n'
        return make_response(body, 200, {'Content-Type': 'text/plain; charset=utf-8'})

    @app.route('/sitemap.xml')
    def sitemap():
        paths = ['/', '/about/', '/about/bylaws/', '/about/officers/', '/join/', '/contests/', '/results/', '/study/',
                 '/links/', '/contact/', '/rules/calculators/', '/50th/']
        for s in D.seasons():
            sm = D.season_summary(s)
            paths.append(f'/contests/{s}/')
            if sm['has_topics']:
                paths.append(f'/contests/{s}/topics/')
            if sm['has_dates']:
                paths.append(f'/contests/{s}/dates/')
            if sm['has_clusters']:
                paths.append(f'/contests/{s}/clusters/')
            if sm['has_officers']:
                paths.append(f'/about/officers/{s}/')
            if sm['has_results']:
                paths += [f'/results/{s}/', f'/results/{s}/teams/', f'/results/{s}/divisions/']
        for r in D.q("SELECT key FROM pages WHERE kind='cluster'"):
            season, n = r['key'].split('/')
            paths.append(f'/contests/{season}/clusters/{n}/')
        for r in D.q("SELECT key FROM pages WHERE kind='contact'"):
            paths.append(f'/contact/{r["key"]}/')
        # Deliberately absent: individual results, student pages and search (names; pending league approval).
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        xml += [f'<url><loc>{site_url(quote(p))}</loc></url>' for p in paths]
        xml.append('</urlset>')
        return make_response('\n'.join(xml), 200, {'Content-Type': 'application/xml; charset=utf-8'})


# --------------------------------------------------------------------------- errors / legacy

def register_errors(app):
    @app.errorhandler(404)
    def not_found(_e):
        new = new_url_for_old_path(request.path)
        if new and new != request.path:
            return redirect(new, 301)
        g.robots = NOINDEX
        return render_template('error.html', title='Page not found', description='', robots=NOINDEX, canonical='',
                               crumbs=[('Home', url_for('home'))], code=404,
                               heading='We couldn’t find that page',
                               message='The page may have moved. Try the links below or search the results archive.'), 404

    @app.errorhandler(405)
    def not_allowed(_e):
        return render_template('error.html', title='Not allowed', description='', robots=NOINDEX, canonical='',
                               crumbs=[('Home', url_for('home'))], code=405, heading='That isn’t allowed here',
                               message='This site only supports viewing pages.'), 405

    @app.errorhandler(413)
    def too_large(_e):
        return render_template('error.html', title='Request too large', description='', robots=NOINDEX, canonical='',
                               crumbs=[('Home', url_for('home'))], code=413, heading='Request too large',
                               message='This site does not accept uploads.'), 413

    @app.errorhandler(500)
    def server_error(_e):
        return render_template('error.html', title='Something went wrong', description='', robots=NOINDEX, canonical='',
                               crumbs=[('Home', url_for('home'))], code=500, heading='Something went wrong',
                               message='An unexpected error occurred. Please try again later.'), 500
