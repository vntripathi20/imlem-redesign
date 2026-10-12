"""Turn the body of an archived old-site page into safe HTML for the new site.

The archive is trusted (it is IMLEM's own content) but old pages use obsolete
tags, unclosed ``<p>``/``<li>`` and site-relative links, so the importer
re-serialises them through an allow-list: unknown tags are dropped (their text
is kept), attributes are reduced to a safe set, links are rewritten to the new
URL scheme, and tables are wrapped so they scroll on small screens.
"""
import posixpath
import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

from .legacy import new_url_for_old_path, season_id

ALLOWED = {
    'a', 'b', 'strong', 'i', 'em', 'u', 'tt', 'small', 'sup', 'sub', 'br', 'hr',
    'p', 'ul', 'ol', 'li', 'blockquote', 'span', 'div',
    'h2', 'h3', 'h4', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'caption',
}
VOID = {'br', 'hr'}
CLASSES = {'note', 'center', 'toc', 'tablewrap'}
SELF_HOSTS = {'imlem.org', 'www.imlem.org'}
NAV_LINK = re.compile(
    r'(?:&xlarr;|&xrarr;|<--|-->)?\s*(?:Back to|Forward to|Previous cluster|Next cluster)',
    re.I,
)


class _Sanitizer(HTMLParser):
    def __init__(self, old_path, report):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.old_path = old_path
        self.report = report
        self.season_hint = None
        m = re.search(r'/(\d{6})/', old_path)
        if m:
            self.season_hint = m.group(1)

    # -- links -----------------------------------------------------------
    def _rewrite(self, href):
        href = href.strip()
        if href.startswith('#'):
            return href
        if href.lower().startswith('mailto:'):
            return None
        parsed = urlparse(href)
        if parsed.scheme in ('http', 'https'):
            if parsed.netloc.lower() not in SELF_HOSTS:
                return href
            old = parsed.path or '/'
        elif parsed.scheme:
            return None
        else:
            old = posixpath.normpath(posixpath.join(posixpath.dirname(self.old_path), parsed.path))
            if parsed.path.endswith('/'):
                old += '/'
            # The old 2024-25 dates page links to "201819topics.html" in its own folder.
            m = re.fullmatch(r'/meetinfo/(\d{6})/(\d{6})(topics|datessites)\.html', old)
            if m and m.group(1) != m.group(2) and self.season_hint == m.group(1):
                self.report.append(f'fixed stale link {old} on {self.old_path}')
                old = f'/meetinfo/{m.group(1)}/{m.group(1)}{m.group(3)}.html'
        new = new_url_for_old_path(old)
        if new is None:
            self.report.append(f'unmapped link {href!r} on {self.old_path}')
            return None
        return new + (f'#{parsed.fragment}' if parsed.fragment else '')

    # -- parser events ---------------------------------------------------
    def handle_starttag(self, tag, attrs):
        was_center = tag == 'center'
        tag = {'center': 'div', 'font': None, 'dir': 'ul'}.get(tag, tag)
        if tag not in ALLOWED:
            return
        a = dict(attrs)
        out = []
        if tag == 'a':
            if a.get('name') and not a.get('href'):
                out.append(f' id="{escape(re.sub(r"[^A-Za-z0-9_-]", "", a["name"]))}"')
            else:
                new = self._rewrite(a.get('href') or '')
                if new is None:
                    # mailto / unmapped: keep the text, drop the link
                    self.stack.append(('a-dropped', 'span'))
                    return
                out.append(f' href="{escape(new, quote=True)}"')
                if new.startswith('http'):
                    out.append(' rel="noopener" class="external"')
        if a.get('id') and re.fullmatch(r'[A-Za-z0-9_-]+', a['id']):
            out.append(f' id="{a["id"]}"')
        cls = {c for c in (a.get('class') or '').split() if c in CLASSES}
        if was_center:
            cls = {'center'}
        if cls and tag != 'a':
            out.append(f' class="{" ".join(sorted(cls))}"')
        for k in ('colspan', 'rowspan'):
            if tag in ('td', 'th') and (a.get(k) or '').isdigit():
                out.append(f' {k}="{a[k]}"')
        if tag == 'table':
            self.out.append('<div class="table-scroll">')
        self.out.append(f'<{tag}{"".join(out)}>')
        if tag not in VOID:
            self.stack.append((tag, tag))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = {'center': 'div', 'dir': 'ul'}.get(tag, tag)
        if tag in VOID:
            return
        names = [t for t, _ in self.stack]
        if tag == 'a' and 'a-dropped' in names:
            tag = 'a-dropped'
        if tag not in names:
            return
        while self.stack:
            t, real = self.stack.pop()
            if real != 'span' or t != 'a-dropped':
                self.out.append(f'</{real}>')
                if real == 'table':
                    self.out.append('</div>')
            if t == tag:
                break

    def handle_data(self, data):
        self.out.append(escape(data))

    def result(self):
        while self.stack:
            t, real = self.stack.pop()
            if t != 'a-dropped':
                self.out.append(f'</{real}>')
                if real == 'table':
                    self.out.append('</div>')
        return ''.join(self.out)


def extract_body(html):
    """Content between the page <h1> and the trailing 'Back to…' links."""
    m = re.search(r'</h1>', html, re.I)
    body = html[m.end():] if m else html
    body = re.split(r'</body>', body, flags=re.I)[0]
    # Cut everything from the trailing "Back to …" block onward.
    idx = [mm.start() for mm in re.finditer(r'<a href="[^"]*">\s*Back to', body)]
    if idx:
        tail = idx[-1]
        # include a directly preceding &nbsp; paragraph
        body = body[:tail]
    return body


def clean(html, old_path, report):
    body = extract_body(html)
    # drop previous/next navigation anchors (replaced by the site's own prev/next)
    body = re.sub(
        r'<a\b[^>]*>\s*' + NAV_LINK.pattern + r'[^<]*</a>\s*(?:/\s*)?(?:<br\s*/?>)?',
        '', body, flags=re.I,
    )
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    body = re.sub(r'(<p>\s*(?:&nbsp;|\s)*)+(?=<p>|\s*$)', '', body, flags=re.I)
    s = _Sanitizer(old_path, report)
    s.feed(body)
    s.close()
    out = s.result()
    out = re.sub(r'(<p>\s*)+(?=</|$)', '', out)
    return out.strip()


def title_of(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S | re.I)
    if not m:
        return ''
    text = re.sub(r'<br\s*/?>', ' ', m.group(1), flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


__all__ = ['clean', 'title_of', 'season_id']
