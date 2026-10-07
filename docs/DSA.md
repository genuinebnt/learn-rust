# anneal · DSA: the NeetCode tracker

The DSA section is being rebuilt as a tracker over the NeetCode lists. This file records the owner's decisions and
the progress; update it as work lands.

## Decisions (owner, 2026-10-07)

| # | Decision |
|---|---|
| 1 | **No AI features** in anneal. The assistant was removed (commit `a0164bf`); 0007 dropped its tables and stored key. |
| 2 | **DSA is the NeetCode lists only:** Blind 75, NeetCode 150, NeetCode 250 and NeetCode All. No custom DSA problems, no editor, no runner, no tests. |
| 3 | **No JavaScript and no SQL problems.** NeetCode's JavaScript pattern and LeetCode's Database problems are left out. LeetCode Premium problems are kept, marked, and can be hidden with a filter. |
| 4 | **Remove the old DSA content and its progress:** tracks D1–D12 (303 problems) and their history (2 solves and 2 reviews in production, both from 2026-09-29). Rust tracks are unaffected. |
| 5 | **Each problem links to LeetCode** (to solve it) and to NeetCode's video, and has a **problem page in anneal**: the LeetCode statement and hints (prefilled from LeetCode), intuition, tips and pitfalls, every useful approach (e.g. DFS *and* topological sort) with **Python** solutions and complexity, and the practice problems that share its idea. |
| 6 | **Pattern lessons per category** (e.g. Graphs: DFS recursive vs iterative, BFS, flood fill, multi-source BFS, topological sort, union-find, bipartite; Two Pointers: opposite ends, fast and slow, …): the signals that call for it, a Python template, pitfalls, and its problems with progress. |
| 7 | **Must learn vs practice (owner's definition, 2026-10-07).** *Must learn* is the **first problem that teaches a particular pattern or algorithm**: one per technique. *Practice* is every other problem that uses the same idea **with a twist**. So classification is by *technique* (e.g. topological sort, union-find, fast and slow pointers), not by LeetCode's "similar questions". The techniques are the pattern lessons (decision 6); each has one must-learn problem, and every practice problem points at it. This replaces my first rule, which marked 702 of 943 as must-learn. |
| 8 | **Tags:** LeetCode's topic tags, and company tags limited to four groups: Big Tech, Databases & infra, Trading, Top tech. Companies come from LeetCode Premium's lists as published in two public datasets, merged (liquidslr and snehasishroy). Elastic, Redis and ClickHouse aren't in either, so they can't be tagged. "Recent" means asked in the last six months. |
| 9 | **Progress and spaced repetition:** solve on LeetCode, then log it in anneal: on my own, with help, or couldn't yet. That feeds the existing review ladder (3 → 7 → 21 → 60 days), the streak and the Progress pages. |
| 10 | **Cascading filters in their own panel**, in anneal's style: list, status, idea (must learn / practice), difficulty, pattern, company group → company, LeetCode tags, hide Premium, group by idea. Each option shows the count the other filters leave. |
| 11 | **Goal:** finish the NeetCode 150, then cover the 250's new ideas (its must-learn problems outside the 150), then the rest of All. |
| 12 | **Writing order:** full problem pages for the NeetCode 150 first, then the 250's must-learn problems, then the rest. Practice problems get a short page (the twist versus the problem it practises, plus a solution). |
| 13 | **Mockup first.** The list, problem page and pattern lesson are mocked up for approval before the UI is built. |
| 14 | **No Build section.** The Backend (B1–B6) and Design-in-Rust (M1–M2) tracks were only planned and are dropped; the nav is DSA, Rust and Progress. |
| 15 | **The overall plan:** DSA in Python (this tracker) and Rust for interviews (the Rust tracks) now. A system design section (LLD, HLD, API design) and behavioral prep come later; they're **deferred**, not started. |
| 16 | **Ship after every batch.** After each batch of work: run the checks, commit, push to `master`, and let CI deploy it to the VPS (https://anneal.genuinebasil.dev). Don't let finished work pile up locally. |
| 19 | **Solutions follow LeetCode's template only.** Every solution is `class Solution` with the method signature exactly as LeetCode's Python 3 template gives it (name, parameters and annotations as LeetCode writes them today, e.g. `list[list[int]]`), so it pastes straight into LeetCode. Helpers go inside the method as nested functions or alongside it in the class; imports go at the top as LeetCode allows; the data structures LeetCode defines (`ListNode`, `TreeNode`, `Node`) are not redefined. The template is fetched from LeetCode per problem, and the build checks each solution's signature against it. |
| 20 | **Spaced repetition is the core, so it is FSRS-6** (the official `fsrs` crate), capacity-aware and shaped to the owner's routine: a new problem Mon–Sat, Sunday reviews the week's problems, one older review a weekday, a little practice on Saturday, and never overwhelming (no day above 12). March 2027 is an ideal, not a deadline. Everything is in docs/SPACED_REPETITION.md. |
| 21 | **The plan is customizable (like Educative's tracks).** The owner sets a target date, how many problems are left (the 143 free NeetCode 150 problems, plus a few from the 250, or a custom number) and, per weekday, whether it is a **solve day** (a new problem and reviews), a **practice day** (reviews only) or a **rest day**, with the reviews each day can take. The app works out the problems needed per solve day and per week, the finish date at the chosen pace, and how it compares to the target. The target stays a soft goal: it informs the display and blocks nothing. Settings: `srs.new_days`, `srs.new_per_day`, `srs.target_date`, `srs.capacity` (`reviews::pace`). |
| 22 | **"Next problem" follows tracks, starting wherever the owner starts.** The owner can start a problem in any track; the next one comes from that track, and when it is finished the tracks below it, in order, then round to whatever is left above. Done problems and finished tracks are skipped. Choosing another track restarts the sequence from that track. One rule: the catalog in order, rotated to the chosen starting problem, done problems skipped (`dsa_next::next_up`). |
| 17 | **The DSA home keeps the existing catalog design** (hero with stats, Next up card, grid of cards, right rail). The cramped table is dropped. Additions: the goal cards (NeetCode 150, new ideas in the 250, All) under the hero, doubling as list switches; **pattern cards** in the existing card style; and a **problems view of long cards** where each must-learn card carries its practice problems underneath. |
| 18 | **Filters swap with the rail.** A Filters button (or `f`) replaces the Activity boxes (This week, Recent, Re-solve due, Readiness) with one long card per filter: status, idea, difficulty, pattern, companies (group, then company, plus "asked in the last 6 months"), LeetCode tags (searchable), Premium. Counts account for the other filters. Activity brings the boxes back. |

## Data

`tools/neetcode/build.py` writes `content/dsa/problems.json` from:
- **neetcode.io's own app bundle:** every problem with its pattern, difficulty, video and list membership.
- **LeetCode's public GraphQL API:** number, topic tags, premium flag, similar questions, statement, hints.
- **The two company datasets.**

Results are cached in `tools/neetcode/cache/` (git-ignored); `--refresh` fetches again.

## Progress

- [x] AI features removed (2026-10-07, `a0164bf`).
- [x] Data builder: NeetCode lists, LeetCode tags and similar questions, merged company tags, must learn vs practice.
- [x] Data: `content/dsa/problems.json` built (943 problems: Blind 75, NeetCode 150/250/All; no JavaScript or SQL; 161 need
      LeetCode Premium; 921 carry a company tag). The must-learn rule marks 702 of 943 as must learn, which is probably
      too many for the "All" list: revisit it with the owner before the content is written.
- [x] Spaced repetition: FSRS-6 engine, capacity per weekday, Sunday consolidation, settings, tests and a simulated-learner
      battle test (2026-10-07; docs/SPACED_REPETITION.md). Still to build: the daily plan endpoint and screens, the
      fourth ("easy") log button, quick-recall review mode.
- [x] Build section removed from the nav, routes, planned tracks and Progress areas (2026-10-07).
- [x] Mockup: list with cascading filters, problem page (Course Schedule), pattern lesson (Graphs), built from the real
      data: https://claude.ai/artifact/UsnLenfPBi3rm5nUkihWFL (files `dsa-tracker.html`, `problem.html`,
      `pattern.html` in `docs/design_handoff_anneal/designs/dsa/`; the generator is `tools/neetcode/mockup_home.py`).
      Version 3 (2026-10-07) follows decisions 17 and 18; the problem and pattern pages were approved as they were.
      **Home awaiting approval.** Progress states are made-up examples; the Graphs lesson lists only problems that exist
      in the NeetCode lists; at 1180px and narrower the rail drops below the list, so there Filters should open as a drawer.
- [x] Plan settings and "next problem" logic (2026-10-07): solve, practice and rest days per weekday, pace from the target
      date (`reviews::pace`), and the track-order rule (`dsa_next::next_up`), both pure and tested. Mockup
      `docs/design_handoff_anneal/designs/dsa/plan.html` (live numbers, track order with a start-here pick).
      **Plan screen awaiting approval.** Still to build: the API for these and the screen.
- [ ] Build: content loader and API for the lists, logging and reviews; remove D1–D12 and their progress (`retired`
      ids so the progress guard allows it).
- [ ] Build: list page, problem page, pattern pages.
- [ ] Content: NeetCode 150 problem pages (Python), then the 250's must-learn, then the rest; pattern lessons for all
      18 categories.
