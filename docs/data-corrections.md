# Data corrections

The files in `archive/imlem.org/` are an untouched copy of the old site and are never edited.
Where the old pages contradict each other or contain a rendering problem, the importer and the page
code handle it, and it is listed here.

## Meet dates: one rule, four conflicts

The date printed in a ranking table's column heading sometimes differs from the date on the same
season's Round Topics page. The site shows the Round Topics (schedule) date on every page
(`imlem_site/db.py`, `meet_labels`). The ranking page's own label is used only if the schedule has no date.

| Season, meet | Old site disagrees on | Shown |
|---|---|---|
| 2018-19, Meet 1 | overall team page says Oct. 15, 2018 | Oct. 25, 2018 |
| 2022-23, Meet 2 | overall team page says Dec. 2, 2022 | Dec. 8, 2022 |
| 2024-25, Meet 5 | individual page says Apr. 4, 2025 | Apr. 3, 2025 |
| 2025-26, Meet 3 | overall team page says Jan. 4, 2026 (a Sunday) | Jan. 8, 2026 |

In every case two of the three sources agree on the date shown (for 2025-26 Meet 3, the by-division
tables agree too). The full comparison, with weekdays, is in
[pending-league-decisions.md](pending-league-decisions.md); the league is asked to confirm the four dates.

## Rendering fix (not a data change)

Round labels such as `Round&nbsp;1` were stored with the HTML entity still encoded and showed up
literally on the round-topics pages. The importer now decodes HTML entities in the text it stores.

## Database rebuilds

`data/imlem.sqlite` is generated and stamped with `IMPORTER_VERSION`. When the importer changes,
older databases are rebuilt automatically on startup. Builds go to a per-process temporary file so
two workers starting at once cannot corrupt each other's build.
