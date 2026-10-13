import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imlem_site.web import create_app  # noqa: E402


@pytest.fixture(scope='session')
def app(tmp_path_factory):
    db = tmp_path_factory.mktemp('db') / 'imlem.sqlite'      # built fresh from archive/, never touches data/
    app = create_app({'TESTING': True, 'DB_PATH': db, 'SITE_URL': 'https://example.test'})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
