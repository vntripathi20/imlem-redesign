"""Small server-rendered SVG charts (no JavaScript needed to draw them).

Each chart is a single series, so it has no legend; the heading above it names what is plotted and
every chart sits next to a table with the same numbers. Hover tooltips come from static/js/charts.js
(data-tip attributes) with an SVG <title> fallback.

Mark specs: 2px lines with round joins, 8px markers with a 2px surface ring, columns no wider than
24px with a 4px rounded top and a square baseline, 1px solid recessive gridlines.
"""
from html import escape
from math import ceil, floor, log10

INK = '#12294d'          # series colour: the league navy
GRID = '#e3e8f0'
AXIS_TEXT = '#4b5a72'
SURFACE = '#ffffff'


def _nice_step(span, target=4):
    if span <= 0:
        return 1
    raw = span / target
    mag = 10 ** floor(log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _fmt(v):
    return f'{v:,.0f}' if float(v).is_integer() else f'{v:,.1f}'


def _rounded_top_bar(x, y, w, h, r=4):
    r = min(r, h, w / 2)
    return (f'M{x:.1f},{y + h:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} '
            f'H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} V{y + h:.1f} Z')


def columns(points, *, label, unit='', height=220, highlight=None):
    """Column chart. points: [(category, value)]. highlight: category whose value is labelled."""
    points = [(c, v) for c, v in points if v is not None]
    if not points:
        return ''
    w_slot, pad_l, pad_r, pad_t, pad_b = 56, 44, 12, 22, 34
    width = pad_l + pad_r + w_slot * len(points)
    top = max(v for _, v in points)
    step = _nice_step(top)
    ymax = ceil(top / step) * step or 1
    plot_h = height - pad_t - pad_b
    y = lambda v: pad_t + plot_h * (1 - v / ymax)  # noqa: E731
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}" '
           f'preserveAspectRatio="xMinYMid meet">']
    t = 0
    while t <= ymax + 1e-9:
        out.append(f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l - 8}" y="{y(t) + 4:.1f}" text-anchor="end" class="tick">{_fmt(t)}</text>')
        t += step
    bar_w = min(24, w_slot - 16)
    peak = max(points, key=lambda p: p[1])[0]
    for i, (cat, v) in enumerate(points):
        cx = pad_l + w_slot * i + w_slot / 2
        x0, top_y = cx - bar_w / 2, y(v)
        tip = f'{cat}: {_fmt(v)}{unit}'
        out.append(f'<g class="mark" data-tip="{escape(tip)}"><title>{escape(tip)}</title>'
                   f'<rect x="{cx - w_slot / 2:.1f}" y="{pad_t}" width="{w_slot}" height="{plot_h}" fill="transparent"/>'
                   f'<path d="{_rounded_top_bar(x0, top_y, bar_w, y(0) - top_y)}" fill="{INK}"/></g>')
        if cat in (highlight, peak):
            out.append(f'<text x="{cx:.1f}" y="{top_y - 6:.1f}" text-anchor="middle" class="val">{_fmt(v)}</text>')
        out.append(f'<text x="{cx:.1f}" y="{height - 12}" text-anchor="middle" class="tick">{escape(_short(cat))}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def rank_line(points, *, label, field_sizes=None, height=240):
    """Line chart of a finishing position over seasons, 1st at the top. points: [(season, rank|None)]."""
    pts = [(c, v) for c, v in points]
    vals = [v for _, v in pts if v is not None]
    if not vals:
        return ''
    w_slot, pad_l, pad_r, pad_t, pad_b = 72, 48, 28, 22, 34
    width = pad_l + pad_r + w_slot * max(len(pts) - 1, 1)
    worst = max(vals)
    # Show at least 1st to 5th so a slip from 1st to 2nd does not read as a cliff.
    worst = max(worst, 5)
    step = max(1, int(round(_nice_step(worst - 1))))   # ranks are whole numbers
    ymax = max(ceil(worst / step) * step, step)
    plot_h = height - pad_t - pad_b
    y = lambda v: pad_t + plot_h * ((v - 1) / (ymax - 1 if ymax > 1 else 1))  # noqa: E731
    x = lambda i: pad_l + (w_slot * i if len(pts) > 1 else w_slot / 2)  # noqa: E731
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}" '
           f'preserveAspectRatio="xMinYMid meet">']
    ticks = [1] + [t for t in range(step, ymax + 1, step) if t > 1]
    for t in ticks:
        out.append(f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l - 8}" y="{y(t) + 4:.1f}" text-anchor="end" class="tick">{_ordinal(t)}</text>')
    # one path per unbroken run of seasons, so a missed season shows as a gap
    run = []
    for i, (_, v) in enumerate(pts + [(None, None)]):
        if v is not None:
            run.append(f'{x(i):.1f},{y(v):.1f}')
        elif run:
            if len(run) > 1:
                out.append(f'<polyline points="{" ".join(run)}" fill="none" stroke="{INK}" stroke-width="2" '
                           f'stroke-linejoin="round" stroke-linecap="round"/>')
            run = []
    best = min(vals)
    last_i = max(i for i, (_, v) in enumerate(pts) if v is not None)
    for i, (cat, v) in enumerate(pts):
        out.append(f'<text x="{x(i):.1f}" y="{height - 12}" text-anchor="middle" class="tick">{escape(_short(cat))}</text>')
        if v is None:
            continue
        of = f' of {field_sizes[cat]}' if field_sizes and field_sizes.get(cat) else ''
        tip = f'{cat}: {_ordinal(v)}{of}'
        out.append(f'<g class="mark" data-tip="{escape(tip)}"><title>{escape(tip)}</title>'
                   f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="12" fill="transparent"/>'
                   f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="4.5" fill="{INK}" stroke="{SURFACE}" stroke-width="2"/></g>')
        if i == last_i or (v == best and i == min(j for j, (_, w) in enumerate(pts) if w == best)):
            out.append(f'<text x="{x(i):.1f}" y="{y(v) - 10:.1f}" text-anchor="middle" class="val">{_ordinal(v)}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def _short(season):
    # '2025-26' -> '25-26' keeps eleven seasons readable on a phone
    return season[2:] if isinstance(season, str) and len(season) == 7 and season[4] == '-' else str(season)


def _ordinal(n):
    n = int(n)
    suf = 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suf}'


ordinal = _ordinal
