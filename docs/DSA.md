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
| 7 | **Must learn vs practice (owner's definition, 2026-10-07).** *Must learn* is the **first problem that teaches a particular pattern or algorithm**: one per technique. *Practice* is every other problem that uses the same idea **with a twist**. So classification is by *technique* (e.g. topological sort, union-find, fast and slow pointers), not by LeetCode's "similar questions". The techniques are the pattern lessons (decision 6); each has one must-learn problem, and every practice problem points at it. This replaces my first rule, which marked 702 of 943 as must-learn. **Built (2026-10-07):** 162 techniques across the 18 patterns; every problem belongs to exactly one. 100 of them are first met in the NeetCode 150 (55 of those in Blind 75), 31 more in the rest of the 250 (its new ideas), 31 only in All. The 150 therefore has 100 must-learn and 50 practice problems; the 250 adds 31 must-learn. A free problem is preferred over a Premium one as a must-learn (only Encode and Decode Strings stays Premium, the only member of its technique in the 150). Assignments: `tools/neetcode/techniques.py` (taxonomy, the 150 by hand) and `assign_rest.py` (the other 793, by hand; similar-question links only place problems added later). `problems.json` gains `technique`, `order` (NeetCode's order) and a top-level `techniques` list. |
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
| 23 | **Practice tracks (owner, 2026-10-07; supersedes the "no custom DSA problems, editor or runner" part of decision 2).** Each topic gets a handwritten **practice track** of independent problems (not from LeetCode) that make the pattern stick and help finish the NeetCode problems, solved in anneal itself (editor, runner, tests). **Order:** per topic, the NeetCode problems with their lessons, then that topic's practice track **in Python**, until every topic is covered; **then the same practice tracks in Rust**, topic by topic; then the other areas (system design and so on). A practice problem **unlocks when its LeetCode problem has been attempted**; one marked `warmup` (it works as a prerequisite) **also opens while that LeetCode problem is coming up next**, so it can be done beforehand. After each topic's track comes a practice session. Practice problems are **not part of spaced repetition** (no reviews, no readiness credit from them). Topic order: Graphs, then DP, then the rest. Open: what counts as "attempted" (recommended: any log, including "not yet"), and the screens need a mockup first. |
| 24 | **Practice is LeetCode problems, not handwritten ones (owner, 2026-10-07; supersedes the "handwritten" part of decision 23).** The practice for each pattern is a list of **other LeetCode problems** (there are thousands beyond the NeetCode lists) that the owner solves on LeetCode, chosen to drill the technique. **Answers:** the in-app handwritten practice is replaced (the P1–P3 tracks stay in the repo and in git history, still loaded, no longer linked; `/api/dsa/handwritten/{pattern}` still serves them); practice problems are logged like the NeetCode ones (✓ on my own, ½ with help, ✗ not yet) but **schedule no reviews, give no readiness and never move "next problem"**; the Practice tab is always visible, **grouped by technique**, each group saying which NeetCode must-learn problem teaches it; about 4 per technique, **free problems only**, taken from outside the NeetCode lists. **Built:** `tools/neetcode/practice.py` picks them (LeetCode similar-question links in both directions, topic tags the technique's problems share, company popularity, at most one Hard per technique) into `content/dsa/practice.json` (607 problems for 157 of 162 techniques); they load as hidden `practice_tracks`, so they never count toward a list. Matching to a technique is by tag and links, so some fits are loose; `PICKS` and `DROP` in `practice.py` override it. Order of topics stays: Backtracking, Trees, Tries, Linked List, Heap, then Math and Bits (lessons only now). |
| 25 | **Mock interview (owner, 2026-10-07; approved).** A configurable timed round at `/dsa/mock`, replacing the "Mock interview" nav stub (DSA first; a Rust round later). The owner sets: lists (NeetCode 150 / 250 / All / Practice), history (everything, not attempted, attempted, solved on my own, due for review), topics (include / exclude per pattern), companies (group and company, optionally recent only), a difficulty mix or a plain count, and **timers** (countdown for the round, countdown per problem, or a stopwatch; strict no-pause; time warnings; end at 0:00 or run into overtime). The app draws random problems from the matching pool when the round starts (uniform, favour weak ones, or favour often-asked); problems are solved on LeetCode and logged ✓ / ½ / ✗ like any attempt (NeetCode problems schedule reviews as usual, practice problems none); blind mode hides topic, tags and companies until a problem is logged. Mockup: the "Anneal Mock Rounds" artifact. **Built (2026-10-07):** `web/src/pages/MockPage.tsx`, rules in `web/src/mock.ts` (tested with `node --test web/src/mock.test.ts`), `crates/api/src/mock.rs` (`GET /api/dsa/mock`, `PUT /api/dsa/mock/config`, `POST /api/dsa/mock/rounds`, table `mock_rounds`). Differences from the mockup: skipping a problem logs nothing (so it never creates an attempt or a review), and there is no tone, only the banner and the clock in the tab title. A round in progress survives a reload (kept in `localStorage`). |
| 26 | **Quick-recall review session (owner, 2026-10-07; approved and built).** `/dsa/review` takes today's reviews (`plan.review_ids`) one at a time: recall first (title, difficulty, last result, recall chance; technique and tags hidden), a six-minute suggestion, a scratch sketch box (not saved), then "Show the approach" reveals the idea and solution, and four grades (Again, Hard, Good, Easy) show when each would bring the problem back and log like ✗ ½ ✓ ⚡. Skip moves a problem to the end of the queue; keys 1 to 4 and Space; a summary at the end; practice problems never appear. Needs a small endpoint that previews the next interval for each grade. Mockup: the "Anneal Quick Recall" artifact. Built: `web/src/pages/DsaProblemPage.tsx`, `styles/problem.css`. Approaches also accept optional `time_why` and `space_why` (why the time and space are what they are), shown under the complexity chips. |
| 27 | **Problem page redesign (owner, 2026-10-08; approved, built).** The page was a narrow left-hugging column with a wide empty right side and buttons of different heights. New: a centred header band (title, difficulty, idea, lists, tags) with a section bar (Problem, Hints, Idea, Approaches, Tips); a reading column; and one sticky right rail with "Solve on LeetCode" and "NeetCode's video" at the same height, four equal log tiles that say when each result brings the problem back, a standing gauge (recall, next review), the problems that share the idea, and the companies; previous and next problem in the pattern; the rail moves to the top on a phone. Needs `GET /api/dsa/problems/{id}/preview` (the four dates for any problem). Mockup: the "Anneal Problem Page" artifact. Not built until approved. |
| 28 | **Calendar (owner, 2026-10-08; proposed, mockup awaiting approval).** A month calendar where every day is a problem day, a practice day or a break. The weekly routine gives the default and the owner overrides single dates, ranges or whole weeks; only the overrides are stored (`calendar_overrides`), and the plan is a pure function of routine, overrides, history and the goal queue, so a practice week pushes the rest of the queue a week later and removing the override puts it back. Reviews are placed by a cost function (early cheaper than late, steep over a day's capacity, never on a break), so a short break pulls reviews earlier and a long one spreads them afterwards. Hovering an edit shows its impact first (finish date, problems moved, reviews re-placed). Past days are never rewritten and are drawn by outcome (solved on my own, with help, couldn't, missed, break); the rail summarises the last eight weeks. Reference implementation and tests: the mockup's `algo.js`. Not built until approved. |
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
      LeetCode Premium; 921 carry a company tag). Must learn vs practice now follows decision 7's technique rule (162 must learn, 781 practice).
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
- [x] Technique classification (2026-10-07): 162 techniques, all 943 problems assigned, must learn = first problem of a
      technique (decision 7).
- [x] Build, backend (2026-10-07, `7fbdd01`): the lists load as 18 tracks (`lc-<slug>`), D1-D12 removed and listed in
      `content/retired.txt` (progress purged at startup; preflight and the safety script allow it), `GET /api/dsa`,
      `POST /api/dsa/problems/{id}/log`, `POST /api/dsa/start`, plan settings with a goal.
- [x] Build, screens (2026-10-07): the home as mocked up (`/dsa`: goals, next up, patterns/problems, Activity|Filters rail,
      `f`), a problem page (`/d/<slug>`: LeetCode and video links, the idea, practice, companies, log buttons) and the
      plan (`/dsa/plan`, saved to `settings.srs`). **Usable now.** The written pages, pattern lessons, statement and hints, the fourth button and the Filters drawer were built later (below).
- [x] Written pages, first pattern (2026-10-07): Arrays & Hashing's nine NeetCode 150 problems (`content/dsa/pages/<slug>.toml`:
      intuition, tips, approaches in Python with complexity). `tools/neetcode/check_pages.py` checks every solution against
      LeetCode's real Python 3 template (`templates.py` fetches it; Premium templates are typed in
      `premium_templates.json`) and runs it against brute-force references (`page_tests.py`). Shown on the problem page
      with approach tabs, highlighting and a copy button. Company pills filter the list and "+n" expands in place.
- [x] Written pages, 99 of the 150 (2026-10-07; Backtracking added): Arrays & Hashing, Two Pointers, Sliding Window, Stack, Graphs, Advanced
      Graphs, Greedy, Intervals, 1-D DP and 2-D DP. The owner's order is a topic's lessons, then its Python practice track,
      then the next topic. **Next: DP practice track in Python**, then back to Binary Search, Linked List, Trees, Heap,
      Backtracking, Tries, Math and Bits (each followed by its practice track), then the Rust practice tracks. The six
      Premium templates are typed from memory (`premium_templates.json`).
- [x] Practice tracks, machinery (2026-10-07): Python in the sandbox runner (harness, syntax/indent errors with a line,
      check mismatches, timeouts), practice problems as section P tracks (`language = "python"`, `unlocked_by`, `warmup`),
      locked until their LeetCode problem is logged (423 from the API), no reviews, the Practice tab
      (`/dsa/practice/<pattern code>`) and "practice n/m" on pattern cards. The workspace and editor are language-aware:
      Python mode, no language server, formatter, lanes or scratch file. Editor behaviour is checked in a real browser by
      `tools/ui-keys.mjs` with `tools/ui-python-editor.json` (normal mode), `ui-python-editor-vim.json` (Vim) and
      `ui-python-flow.json` (run, syntax error, submit); they need a throwaway database, see docs/PRACTICE.md.
- [x] Graphs practice track in Python (2026-10-07): `content/tracks/p1-graphs-practice`, 11 problems (flood fill, painting,
      copying a network, multi-source BFS, fire spread, border search, enclosed lakes, topological order, import cycles,
      union-find, knight moves). `anneal verify P1` passes (solution passes, starter fails, every wrong solution is
      rejected). All 11 solutions were typed by hand into the real editor in headless Chrome and solved through the
      sandbox. Also checked: Python inside the Docker sandbox (no network, read-only root, timeouts).
- [x] DP practice track in Python (2026-10-07): `content/tracks/p2-dp-practice`, 13 problems (Hopscotch, Toll Road, Paths Around
      Rocks, Spaced Picks, Message Splits, Limited Bills, Dice Totals, Trade With a Fee, Fair Shares, Delete to Match,
      Palindrome Cuts, Box Chain, Chain Multiplication). `anneal verify P2` passes. Each is opened by logging its LeetCode
      problem(s); the ones marked warm-up also open while that problem is next up.
- [x] Binary Search lessons (7) and its Python practice track (2026-10-07): `content/tracks/p3-binary-search-practice`, 10 problems
      (First Bad Build counts your calls, Integer Square Root, Count in Range over huge ranges, Shipping Capacity, Find in
      a Table, Rotation Count, Find a Peak, Running Balance, Fair Split, Kth of Two Lists). `anneal verify P3` passes and all
      ten solutions were typed into the real editor and solved. Found and fixed on the way: a timeout landing in the same
      instant a test finished could kill the Python harness (now caught and reported as a timeout).
- [x] Practice is LeetCode problems (decision 24, 2026-10-07): 607 free problems outside the NeetCode lists, about 4 per
      technique (`tools/neetcode/{problemset,similar,practice}.py` -> `content/dsa/practice.json`), the Practice tab grouped
      by technique with ✓ / ½ / ✗ logging and no reviews, "practice n/m" on pattern cards. Checked in the browser
      against a throwaway database (a ✓ writes an attempt and no review).
- [x] Trees lessons (2026-10-07): the 15 NeetCode 150 problems, 29 approaches, checked against brute-force references on
      random trees (`page_tests.py` gained `TreeNode`, `ListNode`, a level-order builder and random tree/BST generators; 25
      seeded bugs were all caught).
- [x] Tries (3) and Linked List (11) lessons (2026-10-07): 14 problems, 27 approaches; checks cover pointer identity (same nodes
      relinked, deep copy shares nothing, input array untouched) and design-class behaviour against models; 34 seeded bugs caught.
- [x] Heap (7), Math & Geometry (8) and Bit Manipulation (7) lessons (2026-10-07): 22 problems, 47 approaches, checked against
      brute-force references (Task Scheduler against a breadth-first search over states, Detect Squares and Design Twitter
      against models, `myPow` with a time limit for huge exponents); 57 seeded bugs, the 7 survivors are equivalent code.
      **Every NeetCode 150 problem now has a checked page (150 of 150).**
      **Next: your call. Look over the lessons and the mock screen, and say what to change. Open items below. The Rust practice
      tracks and system design need re-scoping under decision 24.**
- [x] The NeetCode 250's 31 must-learn problems (2026-10-07): 31 pages, 61 approaches, same checking (Mountain Array with a
      100-call limit, Word Break II with a no-answer case that needs memoizing, Matchsticks with a hard negative). Every
      NeetCode 250 must-learn problem and the whole NeetCode 150 now have checked pages (181).
- [x] Mock interview (decision 25, 2026-10-07): setup with lists, history, topics, companies, difficulty mix, timers and draw
      weighting; the live round with its clocks; the result and past rounds. Checked in a browser against a throwaway database.
- [x] Pattern lessons, machinery (2026-10-07): `content/dsa/lessons/<pattern>.toml` (per technique: signals, a Python template,
      pitfalls), `tools/neetcode/check_lessons.py` (the template parses, has no undefined names, lines fit, and runs its test in
      `lesson_tests.py`), `GET /api/dsa/patterns/{code}`, the Patterns tab (`/dsa/patterns/<code>`, linked from the pattern
      cards and the Problems / Practice tabs). All 162 techniques have a lesson, each template run by a behaviour test (32 seeded bugs: the survivors were equivalent or speed-only).
- [x] The NeetCode 250's 69 practice problems (2026-10-07): short pages with a checked solution and the twist against the problem
      they practise, same checking as the others (36 seeded bugs, the 3 survivors are equivalent code). **All 250 NeetCode
      problems now have a checked page (250 of 250), and all 162 techniques a lesson.**
- [x] The fourth log button and the Filters drawer (2026-10-07): ⚡ "instant" (grade easy) beside ✓ ½ ✗ on the home cards (review problems only; practice
      problems have no reviews), and Filters open as a drawer from the right at 1180px and narrower (Esc or the button closes it).
- [x] Quick-recall review session (decision 26, 2026-10-07): `/dsa/review`, one due problem at a time with recall first, the approach on request, four grades with their next dates, a summary; checked in a browser against a throwaway database.
- [x] LeetCode statement and hints on the problem page (decision 5, 2026-10-07): `GET /api/dsa/problems/{id}/statement` fetches them from LeetCode
      the first time (`ANNEAL_LEETCODE_URL` overrides the endpoint for tests), cleans the HTML (`ammonia`), keeps it in `dsa_statements`
      for 30 days and serves an older copy if LeetCode is unreachable; Premium problems say so. The page shows PROBLEM and
      HINTS (one at a time) above the idea.
- [x] Editor ligatures (2026-10-08): off by default (they flickered while typing and the cursor is placed per character), with a Ligatures
      switch in the editor settings (`ligatures` in `settings.editor`); static code (`code`, `pre`, `kbd`) never uses them, so `!=` is no longer drawn as ≠.
- [ ] Content: pages for the rest of the 943 (the problems only in NeetCode All, 693 of them), if you want them. They are
      practice-level and the Practice tab already points at LeetCode problems, so this is optional.
