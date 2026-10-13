import pytest

from imlem_site import sanitize


def test_security_headers(client):
    resp = client.get('/')
    h = resp.headers
    assert h['X-Content-Type-Options'] == 'nosniff'
    assert h['X-Frame-Options'] == 'DENY'
    assert "default-src 'self'" in h['Content-Security-Policy'] and "script-src 'self'" in h['Content-Security-Policy']
    assert 'frame-ancestors' in h['Content-Security-Policy']
    assert h['Referrer-Policy']


@pytest.mark.parametrize('method', ['post', 'put', 'delete', 'patch'])
def test_site_is_read_only(client, method):
    for path in ['/', '/results/', '/study/', '/contact/', '/results/search/']:
        resp = getattr(client, method)(path, data={'x': 'y'})
        assert resp.status_code in (404, 405), (method, path)


@pytest.mark.parametrize('path', ['/api/login', '/api/me', '/api/users', '/api/upload-file', '/api/divisions'])
def test_old_admin_api_is_gone(client, path):
    assert client.get(path).status_code == 404
    assert client.post(path, json={'email': 'admin@imlem.org', 'password': 'admin123'}).status_code in (404, 405)


def test_no_default_accounts_or_secrets_in_repo():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    assert not (root / 'data' / 'users.json').exists()
    for f in list(root.glob('*.py')) + list((root / 'imlem_site').glob('*.py')) + list(root.glob('*.md')):
        text = f.read_text(encoding='utf-8')
        assert 'admin123' not in text and 'coach123' not in text, f


@pytest.mark.parametrize('path', [
    '/files/../app.py', '/files/..%2fapp.py', '/uploads/../app.py', '/uploads/..%2f..%2fapp.py',
    '/images/../app.py', '/files/%2e%2e/app.py', '/static/../app.py',
])
def test_no_path_traversal(client, path):
    resp = client.get(path)
    assert resp.status_code in (301, 308, 400, 404)
    assert b'create_app' not in resp.data


def test_request_bodies_are_capped(client):
    resp = client.post('/', data=b'x' * (200 * 1024), content_type='application/octet-stream')
    assert resp.status_code in (405, 413)


def test_sanitizer_drops_scripts_and_dangerous_attributes():
    report = []
    html = ('<h1>t</h1><p onclick="x()">hi <script>alert(1)</script><a href="javascript:alert(1)">bad</a>'
            '<a href="http://example.com/" onmouseover="x">ok</a><img src=x onerror=alert(1)><style>p{}</style>')
    out = sanitize.clean(html, '/leagueinfo/x.html', report)
    assert '<script' not in out and 'onclick' not in out and 'onerror' not in out and 'javascript:' not in out
    assert 'onmouseover' not in out and '<img' not in out
    assert 'href="http://example.com/"' in out and 'rel="noopener"' in out


def test_sanitizer_rewrites_old_links_and_drops_mailto():
    report = []
    html = ('<h1>t</h1><p><a href="../202526/202526topics.html#1">x</a> '
            '<a href="mailto:a@b.c">mail</a> <a href="http://www.imlem.org/statistics/index.html">s</a>')
    out = sanitize.clean(html, '/meetinfo/202627/202627topics.html', report)
    assert 'href="/contests/2025-26/topics/#1"' in out
    assert 'mailto' not in out and 'mail' in out
    assert 'href="/results/"' in out
