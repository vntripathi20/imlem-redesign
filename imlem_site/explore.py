"""Pages built on top of the results archive and the season schedules:

* /schools/ and /schools/<slug>/      every school's teams and season-by-season record
* /results/records/                    league records and participation over time
* /about/how-meets-work/               a plain-language guide built from the League Bylaws
* /contests/<season>/calendar.ics      the season's meets as a calendar file
* /study/meet/<n>/                     one meet's topics plus every past contest for that meet
"""
from datetime import date, datetime, timedelta, timezone

from flask import abort, make_response, redirect, request, url_for

from . import charts
from . import config as cfg
from . import db as D
from . import stats as S

SUBJECTS = ['Mystery', 'Geometry', 'Number Theory', 'Arithmetic', 'Algebra']


def register_explore(app, render, valid_season):
    # ---- schools --------------------------------------------------------------
    @app.route('/schools/')
    def schools_index():
        all_schools = S.schools()
        latest = D.results_seasons()[0]
        groups = {}
        for s in all_schools:
            groups.setdefault(s['name'][0].upper(), []).append(s)
        return render('schools.html', title='Schools',
                      description='Every school in the IMLEM results archive, with its teams and season-by-season record.',
                      crumbs=[('Results', url_for('results')), ('Schools', None)],
                      groups=sorted(groups.items()), count=len(all_schools), latest=latest,
                      active_count=sum(1 for s in all_schools if s['last'] == latest))

    @app.route('/schools/<slug>/')
    def school_page(slug):
        school = S.school_by_slug(slug)
        if not school:
            abort(404)
        history = S.school_history(school)
        honours = S.school_honours(history)
        seasons = sorted(D.results_seasons())
        field = {h['season']: h['of'] for h in history}
        chart = ''
        main_rows = {h['season']: h['rank_n'] for h in history if h['team'] == school['name']}
        if len(main_rows) >= 2:
            span = [s for s in seasons if school['first'] <= s <= school['last']]
            chart = charts.rank_line([(s, main_rows.get(s)) for s in span],
                                     label=f'{school["name"]} league finish by season', field_sizes=field)
        return render('school_page.html', title=f'{school["name"]} — IMLEM results by season',
                      description=f'{school["name"]} in the IMLEM results archive: league and division finishes, '
                                  f'meet scores and team totals for every season from {school["first"]} to {school["last"]}.',
                      crumbs=[('Results', url_for('results')), ('Schools', url_for('schools_index')), (school['name'], None)],
                      school=school, history=history, honours=honours, chart=chart, ordinal=charts.ordinal,
                      max_meet=S.MAX_TEAM_MEET)

    # ---- records ---------------------------------------------------------------
    @app.route('/results/records/')
    def records():
        r = S.records()
        part = r['participation']
        return render('records.html', title='Records and trends',
                      description=f'IMLEM league records from {r["first"]} to {r["last"]}: highest team scores, '
                                  'league champions, and how many teams and students took part each season.',
                      crumbs=[('Results', url_for('results')), ('Records', None)], r=r,
                      students_chart=charts.columns([(p['season'], p['students']) for p in part],
                                                    label='Students in the results each season', highlight=part[-1]['season']),
                      teams_chart=charts.columns([(p['season'], p['teams']) for p in part],
                                                 label='Teams in the results each season', highlight=part[-1]['season']),
                      avg_chart=charts.columns([(p['season'], p['average']) for p in part],
                                               label='Average team score per meet each season', highlight=part[-1]['season']),
                      slug=S.school_slug_for_team, max_meet=S.MAX_TEAM_MEET)

    # ---- guide -----------------------------------------------------------------
    @app.route('/about/how-meets-work/')
    def guide():
        nxt = D.next_meet()
        season = nxt['season'] if nxt else D.seasons()[0]
        return render('guide.html', title='How IMLEM meets work',
                      description='A guide for students, families and new coaches: teams, the five rounds and the team '
                                  'round, scoring, calculators, meet day and awards, from the League Bylaws.',
                      crumbs=[('About', url_for('about')), ('How meets work', None)],
                      season=season, meets=D.meets_for(season), subjects=SUBJECTS,
                      topics={(r['meet'], r['category']): r['description'] for r in
                              D.q("SELECT meet, category, description FROM rounds WHERE season=?", season)})

    # ---- calendar --------------------------------------------------------------
    @app.route('/contests/<season>/calendar.ics')
    def calendar(season):
        valid_season(season)
        meets = [m for m in D.meets_for(season) if m['date_iso']]
        if not meets:
            abort(404)
        rounds = {}
        for r in D.q('SELECT * FROM rounds WHERE season=? ORDER BY meet, seq', season):
            rounds.setdefault(r['meet'], []).append(r)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        host = (request.host or 'imlem').split(':')[0]
        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//IMLEM//Meet schedule//EN', 'CALSCALE:GREGORIAN',
                 'METHOD:PUBLISH', _ics_text('X-WR-CALNAME', f'IMLEM meets {season}')]
        for m in meets:
            d = date.fromisoformat(m['date_iso'])
            topics = '\\n'.join(
                'Team round' if r['label'].startswith('Team') else
                f'{r["label"]}: {r["category"]}' + (f' ({r["description"]})' if r['description'] else '')
                for r in rounds.get(m['number'], []))
            desc = (f'{"Calculator meet" if m["calculators"] else "No calculators"}.\\n{topics}\\n'
                    f'Meet sites and start times are set by each cluster.')
            lines += ['BEGIN:VEVENT', f'UID:imlem-{season}-meet-{m["number"]}@{host}', f'DTSTAMP:{stamp}',
                      f'DTSTART;VALUE=DATE:{d:%Y%m%d}', f'DTEND;VALUE=DATE:{d + timedelta(days=1):%Y%m%d}',
                      _ics_text('SUMMARY', f'IMLEM Meet {m["number"]}' + (' (calculators)' if m['calculators'] else '')),
                      _ics_text('DESCRIPTION', desc, raw=True),
                      _ics_text('URL', request.url_root.rstrip('/') + url_for('topics', season=season) + f'#meet-{m["number"]}'),
                      'TRANSP:TRANSPARENT', 'END:VEVENT']
        lines.append('END:VCALENDAR')
        body = '\r\n'.join(_fold(line) for line in lines) + '\r\n'
        resp = make_response(body)
        resp.headers['Content-Type'] = 'text/calendar; charset=utf-8'
        resp.headers['Content-Disposition'] = f'attachment; filename="imlem-meets-{season}.ics"'
        return resp

    # ---- study: one meet's practice page ------------------------------------------
    @app.route('/study/meet/<int:number>/')
    def practice(number):
        if number not in range(1, 6):
            abort(404)
        current = D.q("SELECT * FROM rounds WHERE meet=? AND season=(SELECT MAX(season) FROM rounds) ORDER BY seq", number)
        past = D.q('SELECT * FROM meets WHERE number=? ORDER BY season DESC', number)
        nxt = D.next_meet()
        upcoming = D.q1('SELECT * FROM meets WHERE number=? AND date_iso>=? ORDER BY date_iso LIMIT 1',
                        number, date.today().isoformat())
        return render('practice.html', title=f'Practice for Meet {number}',
                      description=f'IMLEM Meet {number} round topics and every past Meet {number} contest to practice with.',
                      crumbs=[('Study materials', url_for('study')), (f'Meet {number}', None)],
                      number=number, rounds=current, past=past, upcoming=upcoming, nxt=nxt,
                      with_pdf=sum(1 for m in past if m['contest_url']), archive_host=cfg.CONTEST_ARCHIVE_HOST,
                      calculators=bool(past and past[0]['calculators']))

    # season switcher target (see the season_switcher macro); only whitelisted pages
    @app.route('/go/')
    def season_go():
        to, season = request.args.get('to', ''), request.args.get('season', '')
        allowed = {'results_season', 'results_teams', 'results_divisions', 'results_individuals', 'season_hub', 'topics'}
        if to not in allowed:
            abort(404)
        valid_season(season)
        return redirect(url_for(to, season=season), 303)

    # old query-string school URL -> the school's own page
    @app.route('/results/school/')
    def school():
        name = request.args.get('name', '').strip()[:100]
        if not name:
            abort(404)
        slug = S.school_slug_for_team(name)
        if not S.school_by_slug(slug):
            abort(404)
        return redirect(url_for('school_page', slug=slug), 301)


def _ics_escape(s):
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def _ics_text(key, value, raw=False):
    # raw: the value already contains literal "\n" escapes and must keep them
    if raw:
        value = value.replace(';', '\\;').replace(',', '\\,')
    else:
        value = _ics_escape(value)
    return f'{key}:{value}'


def _fold(line):
    # RFC 5545: lines longer than 75 octets are folded with CRLF + space
    out, b = [], line.encode('utf-8')
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:   # do not split a UTF-8 character
            cut -= 1
        out.append(b[:cut].decode('utf-8'))
        b = b' ' + b[cut:]
    out.append(b.decode('utf-8'))
    return '\r\n'.join(out)
