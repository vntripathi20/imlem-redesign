"""Rebuild data/imlem.sqlite from archive/imlem.org (never modifies the archive)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imlem_site.importer import build_database  # noqa: E402


def main():
    summary, report = build_database(ROOT / 'archive' / 'imlem.org', ROOT / 'data' / 'imlem.sqlite')
    for season, info in summary.items():
        print(season, info)
    print(f'\n{len(report)} import notes')
    for line in report:
        print(' -', line)


if __name__ == '__main__':
    main()
