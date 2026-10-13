# Pending league decisions and TODOs

Nothing below was invented. Where the old site did not say, the new site shows a visible "pending" note, and the code carries a `TODO(league)` comment (search for it: `grep -rn "TODO(league)"`).

| # | Item | Status | Where in the site / code |
|---|---|---|---|
| 1 | **Student names**: first name + last initial, grade, school. The old site names only some students (e.g. 39 of 1,226 in 2015-16, 107 of 967 in 2025-26). | **Pending league approval.** Until approved, individual rankings, student pages and student search are `noindex` and excluded from `sitemap.xml`. | `imlem_site/config.py` (`STUDENT_NAMES_APPROVED_FOR_INDEXING`), `web.py` |
| 2 | **Current officers.** The most recent officer list on the old site is 2022-23. Contact pages show the same people, labelled with that year. | **Pending confirmation.** No current officer is named by this project. | `config.py` (`OFFICERS_LAST_CONFIRMED`), `templates/contact.html`, `join.html`, `content.html`, `officers_index.html`; contact text itself is in the archive pages `archive/imlem.org/contact/*.html` |
| 3 | **Coaches' Corner.** Password-protected on the old site; not audited or migrated. | Placeholder page ("Coming soon") marked noindex. Send the content when available. | `templates/coaches.html` |
| 4 | **How to join.** The old site only says to contact the president. Fees, deadlines and new-member steps are not stated. | Page explains the old site's process; the missing details are marked. | `templates/join.html` |
| 5 | **50th anniversary.** The old site has only the anniversary image. The Bylaws say the first contest was in March 1965; the old SPA prototype claimed "since 1974". The site states no founding year. | Page shows the mark and quotes the Bylaws; history is marked as not yet supplied. | `templates/anniversary.html` |
| 6 | **Meet sites and times** for 2026-27 and the 2025-26 dates/sites page were never published on the old site. | The home page says sites are set by clusters; no site list is shown. | `templates/home.html`, `topics.html` |
| 7 | **Announcements.** The old site had none. | Empty list; add items in the JSON file. | `data/announcements.json` |
| 8 | **Difficulty levels** for study materials: the old site gives none. | Study topics can be filtered by season, meet number (1 to 5), and subject. No difficulty is claimed. | `templates/study.html` |
| 9 | **Contest PDFs** are hosted by matharchive.org. Per the league's decision they are linked, not mirrored. 2019-20 meet 5 and 2024-25 meet 5 link to nothing on the old site; the new site says so. | Done | `study.html`, `topics.html` |
| 10 | **Four meet dates are inconsistent inside the old site** (table below). The site shows the date from the season's published schedule (the Round Topics page) on every page, and leaves the archive untouched. | **League to confirm the four dates.** If a schedule date is wrong, tell the maintainer; the archive copy stays untouched and a correction goes in the importer. | `imlem_site/db.py` (`meet_labels`), `archive/` |
| 11 | **Division naming** differs by year (e.g. "DaVinci" vs "da Vinci"). Kept as published. | As published | |
| 12 | **Links page** was carried over unchanged and not re-checked. Some external sites may have moved or died. | Marked on the page | `/links/` |
| 13 | **Old site HTTPS** was broken. The new site must be served over HTTPS. | See DEPLOYMENT.md | |

## Meet dates that disagree in the old site's own pages

Found by comparing the date printed in each season's ranking-table headings with the Round Topics page for the same season. In each case two of the three sources agree, and the new site shows that date everywhere. This is a rule, not a judgement about which is "right"; the league should confirm.

| Season, meet | Round Topics page (schedule) | Individual rankings page | Team rankings page | Shown on the new site | Odd one out |
|---|---|---|---|---|---|
| 2018-19, Meet 1 | October 25, 2018 (Thu) | Oct. 25, 2018 | **Oct. 15, 2018** (Mon) | Oct. 25, 2018 | team page |
| 2022-23, Meet 2 | December 8, 2022 (Thu) | Dec. 8, 2022 | **Dec. 2, 2022** (Fri) | Dec. 8, 2022 | team page |
| 2024-25, Meet 5 | April 3, 2025 (Thu) | **Apr. 4, 2025** (Fri) | Apr. 3, 2025 | Apr. 3, 2025 | individuals page |
| 2025-26, Meet 3 | January 8, 2026 (Thu) | Jan. 8, 2026 | **Jan. 4, 2026** (Sun) | Jan. 8, 2026 | team page |

For 2025-26 Meet 3, the by-division team page also says Jan. 8, 2026, so only the overall team page (`202526_team.html`) says Jan. 4. The 2020-21 season has Wednesday and Tuesday meets in its schedule; that is consistent across all of its pages and is left as published.

`tests/test_review_fixes.py` checks that every page shows one date per meet.

## How to replace the migrated officer / contact pages once confirmed

The pages are stored in the `pages` table (kinds `officers`, `contact`) generated from `archive/imlem.org/`. To publish new information, add new files in the same style under `archive/imlem.org/` (for example `leagueinfo/202627/202627officers.html`), extend `imlem_site/legacy.py` if needed, re-run `python scripts/import_archive.py`, set `OFFICERS_LAST_CONFIRMED`, and remove the "pending" notices from the templates.
