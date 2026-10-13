# Data corrections

The files in `archive/imlem.org/` are an untouched copy of the old site and are never edited.
When an old page contains a clear error, the importer (`imlem_site/importer.py`) corrects it while
building the database, and the correction is listed here.

| Season | Where | Old site says | Site shows | Evidence |
|---|---|---|---|---|
| 2025-26 | Overall team rankings, Meet 3 column header | Jan. 4, 2026 | Jan. 8, 2026 | Jan. 4, 2026 is a Sunday. The 2025-26 round-topics page, the individual rankings and all eleven by-division tables give January 8, 2026. |

Rendering fix (not a data change): round labels such as `Round&nbsp;1` were stored with the HTML
entity still encoded and showed up literally on the round-topics pages. The importer now decodes
HTML entities in all cell text.
