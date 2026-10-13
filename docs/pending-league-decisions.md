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
| 10 | **Source inconsistencies kept as-is**: some meet dates differ between the individual and team ranking pages of the same season (e.g. 2025-26 meet 3: Jan. 8 vs Jan. 4). Each page shows the labels from its own source. | Left as published; league may want to correct the source. | `archive/` |
| 11 | **Division naming** differs by year (e.g. "DaVinci" vs "da Vinci"). Kept as published. | As published | |
| 12 | **Links page** was carried over unchanged and not re-checked. Some external sites may have moved or died. | Marked on the page | `/links/` |
| 13 | **Old site HTTPS** was broken. The new site must be served over HTTPS. | See DEPLOYMENT.md | |

## How to replace the migrated officer / contact pages once confirmed

The pages are stored in the `pages` table (kinds `officers`, `contact`) generated from `archive/imlem.org/`. To publish new information, add new files in the same style under `archive/imlem.org/` (for example `leagueinfo/202627/202627officers.html`), extend `imlem_site/legacy.py` if needed, re-run `python scripts/import_archive.py`, set `OFFICERS_LAST_CONFIRMED`, and remove the "pending" notices from the templates.
