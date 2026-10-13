"""Site-wide constants and the places where the league still has to confirm content."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / 'archive' / 'imlem.org'
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = BASE_DIR / 'uploads'
FILES_DIR = BASE_DIR / 'files'

SITE_NAME = 'IMLEM'
SITE_FULL_NAME = 'Intermediate Math League of Eastern Massachusetts'

# TODO(league): the old site's most recent officer list is 2022-23 and its contact pages carry
# the same names. Update both (and docs/pending-league-decisions.md) once the league confirms
# the current officers. Until then the site labels this information with its year.
OFFICERS_LAST_CONFIRMED = '2022-23'

# The old site shows only a first name + last initial, and only for top finishers.
# TODO(league): pending league approval of publishing these names on the new site.
# Until approved, individual results and student search carry noindex and stay out of sitemap.xml.
STUDENT_NAMES_APPROVED_FOR_INDEXING = False

CONTEST_ARCHIVE_HOST = 'matharchive.org'
INDIVIDUALS_PER_PAGE = 100


def env_flag(name, default=False):
    return os.environ.get(name, '1' if default else '0').strip().lower() in ('1', 'true', 'yes', 'on')
