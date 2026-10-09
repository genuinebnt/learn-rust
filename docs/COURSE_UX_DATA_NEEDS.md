# What the course mockups need from the data

For [course-motion.html](mockups/course-motion.html) and its neighbours. "Exists" was checked against `crates/api` and `crates/content` on
2026-10-09. Nothing here is built yet; the choices at the bottom are the owner's.

## Already served

| mockup feature | where it comes from |
|---|---|
| tests-pass popup: tests passed, run time, hints used, next stage | `last_run`, `hints.revealed`, `next` on `GET /courses/{c}/stages/{id}` |
| hint ladder, hidden solution with a reveal | `hints`, `solution` and the reveal endpoints |
| course map, module progress, "UP NEXT", continue ring | `GET /courses/{c}` (projects, modules, stage states) |
| Last run tab: the latest run, failures first, compare needs only two runs | `last_run` (see "run history" for the older ones) |
| concepts per stage and their reading time | `concepts[{id, title, summary, minutes}]` on the stage endpoint |

## Missing, small

| feature | gap | change |
|---|---|---|
| **Run history** (Last run tab: pick an earlier run, compare with the previous) | every run is stored in `course_runs`, but the stage endpoint returns only the newest | return the last 10 runs: `runs: [{id, ok, passed, total, tests, problem, commit_sha, duration_ms, at}]`; one query |
| **Minutes per stage** (stage rows in the left panel) | `stage.toml` has no estimate; concepts have `minutes` | add an optional `minutes` to `stage.toml` and to the stage row; a lint warns when missing. The 163 values would have to be written |
| **Required or optional concepts** | `concepts = [...]` does not say which | `concepts = [...]` stays the required list; add `concepts_optional = [...]`. The linter already checks that each id exists |
| **Show the celebration popup** | no setting | one boolean, `course_celebrate`, in the existing settings; default on |

## Missing, needs a decision

| feature | what it would take | the choice |
|---|---|---|
| **Concept read state** (Concepts tab, right panel, the "1 of 3" ring) | a table `course_concept_state(course, concept, read, read_at)` and `PUT /courses/{c}/concepts/{id}/read`. Reading progress as a percent would also need scroll tracking in the article | read / unread only, or also a percent? I would start with read / unread |
| **Time on a stage and pomodoros** (timer footer) | a table `course_focus(course, stage_id, day, seconds, pomodoros)` and a `POST` the timer sends when a session ends or the page closes | keep the timer purely in the browser (nothing stored), or store it? Storing makes "18 min today" real; the timer works without it |
| **Per-test durations** | the CLI report has only a total, and stable `cargo test` does not time each test | leave out. Nightly's `--report-time` is the only source |

## Remembered in the browser, or on the account

The mockup keeps these in `localStorage` under `anneal:` keys. The right-hand column is what I would move to the account (a `ui` JSON in the
existing settings row) so a second machine behaves the same.

| choice | now | account? |
|---|---|---|
| panel widths, left and right panel collapsed | browser | no: depends on the screen |
| optional sections hidden | browser | yes |
| concepts filter (all / required / optional) | browser | no |
| "don't show the popup again" | browser | yes (the setting above) |
| timer mode and lengths | browser | yes |
| concept read state | browser in the mockup | **yes**, it is progress: table above |
| per-tab scroll positions | memory only | no |

## Order I would build the data in

1. `runs` history and the popup setting: small, unlock the Last run tab and the popup.
2. `concepts_optional` and concept read state: unlock the Concepts tab and the panel card.
3. `minutes` for stages: needs writing, so only when the left panel's durations matter to you.
4. Time on stage: only if you want the number; the timer does not need it.
