"""Follow every internal link reachable from the home page; none may be broken.

Sort/filter/pager variants (``?query``) and per-student pages are template-identical and covered
by test_results.py, so the crawl skips them; otherwise it would visit thousands of 1,000-row pages.
"""
import html as htmllib
import re
from urllib.parse import urldefrag, urlparse

STUDENT = re.compile(r'^/results/[\d-]+/individuals/\d+/$')


def test_no_broken_internal_links(client):
    seen, queue, broken = set(), ['/'], []
    while queue:
        url = urldefrag(queue.pop())[0]
        if url in seen:
            continue
        seen.add(url)
        resp = client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            broken.append((url, resp.status_code))
            continue
        if 'text/html' not in resp.content_type:
            continue
        for href in re.findall(r'href="([^"]+)"', resp.get_data(as_text=True)):
            href = htmllib.unescape(href)
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or href.startswith(('mailto:', '#')):
                continue
            if parsed.query and not href.startswith('/results/school/'):
                continue
            if STUDENT.match(parsed.path):
                continue
            queue.append(href)
    assert not broken, broken[:10]
    assert len(seen) > 250
