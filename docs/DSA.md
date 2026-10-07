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
| 7 | **Must learn vs practice.** Within a NeetCode pattern, problems that LeetCode lists as similar share an idea. The one from the more central list (Blind 75 → 150 → 250 → All, then the lower LeetCode number) is *must learn*; the others are *practice of* it. A problem with no such link is a new idea, so it's must learn too. |
| 8 | **Tags:** LeetCode's topic tags, and company tags limited to four groups: Big Tech, Databases & infra, Trading, Top tech. Companies come from LeetCode Premium's lists as published in two public datasets, merged (liquidslr and snehasishroy). Elastic, Redis and ClickHouse aren't in either, so they can't be tagged. "Recent" means asked in the last six months. |
| 9 | **Progress and spaced repetition:** solve on LeetCode, then log it in anneal: on my own, with help, or couldn't yet. That feeds the existing review ladder (3 → 7 → 21 → 60 days), the streak and the Progress pages. |
| 10 | **Cascading filters in their own panel**, in anneal's style: list, status, idea (must learn / practice), difficulty, pattern, company group → company, LeetCode tags, hide Premium, group by idea. Each option shows the count the other filters leave. |
| 11 | **Goal:** finish the NeetCode 150, then cover the 250's new ideas (its must-learn problems outside the 150), then the rest of All. |
| 12 | **Writing order:** full problem pages for the NeetCode 150 first, then the 250's must-learn problems, then the rest. Practice problems get a short page (the twist versus the problem it practises, plus a solution). |
| 13 | **Mockup first.** The list, problem page and pattern lesson are mocked up for approval before the UI is built. |
| 14 | **No Build section.** The Backend (B1–B6) and Design-in-Rust (M1–M2) tracks were only planned and are dropped; the nav is DSA, Rust and Progress. |
| 15 | **The overall plan:** DSA in Python (this tracker) and Rust for interviews (the Rust tracks) now. A system design section (LLD, HLD, API design) and behavioral prep come later; they're **deferred**, not started. |

## Data

`tools/neetcode/build.py` writes `content/dsa/problems.json` from:
- **neetcode.io's own app bundle:** every problem with its pattern, difficulty, video and list membership.
- **LeetCode's public GraphQL API:** number, topic tags, premium flag, similar questions, statement, hints.
- **The two company datasets.**

Results are cached in `tools/neetcode/cache/` (git-ignored); `--refresh` fetches again.

## Progress

- [x] AI features removed (2026-10-07, `a0164bf`).
- [x] Data builder: NeetCode lists, LeetCode tags and similar questions, merged company tags, must learn vs practice.
- [x] Build section removed from the nav, routes, planned tracks and Progress areas (2026-10-07).
- [ ] Mockup: list with cascading filters, problem page (Course Schedule), pattern lesson (Graphs). **Awaiting approval.**
- [ ] Build: content loader and API for the lists, logging and reviews; remove D1–D12 and their progress (`retired`
      ids so the progress guard allows it).
- [ ] Build: list page, problem page, pattern pages.
- [ ] Content: NeetCode 150 problem pages (Python), then the 250's must-learn, then the rest; pattern lessons for all
      18 categories.
