# Must-solve problems beyond the NeetCode lists: plan

Status: **plan, nothing built** (2026-10-10). It needs the owner's answers to the questions in section 9, and a mockup (docs/DSA.md
decision 13) before any screen is built.

The owner's request: find the problems that are worth solving **beyond what the NeetCode lists already cover**, judged by
**how often large companies ask them** and by **how important and frequent the concept is**, and say how they are tagged, shown and
stored.

## 1. What the data says

Sources: the app's own lists (`content/dsa/problems.json`, 943 problems, and `content/dsa/practice.json`, 607 LeetCode problems outside the
lists that already drill a technique); LeetCode's own problem index (4,073 problems with their topic tags); and a public per-company
frequency dataset (github.com/liquidslr/leetcode-company-wise-problems: for each company, every problem it asked, with a frequency
from 0 to 100 relative to that company's most-asked problem, and a "last six months" file). 45 large companies were used.

| | count |
|---|---|
| LeetCode problems asked by at least one of the 45 companies, outside the NeetCode lists (no SQL, shell or concurrency) | 1,967 |
| of those, already in the app's practice list | 579 |
| **Tier A** (see section 2) | 331 (198 already in the app, **133 new**) |
| **Tier B** | 310 (125 already in the app, **185 new**) |
| new Tier A/B that are easy warm-ups (array, string, hash table only) | 80 of 318 |
| new Tier A/B that are medium or hard and not warm-ups | 238 |
| new Tier A that are medium or hard and not warm-ups | 73 |

Where the new ones sit (Tier A or B): Arrays & Hashing 123, Math & Geometry 52, Dynamic Programming 44, Binary Search 27, Graphs 19,
Greedy 16, Heap 9, Two Pointers 8, Bit Manipulation 7, Sliding Window 4, others 5. The shape matters: **the app already holds most of the
high-frequency problems** (the highest scorers outside the lists, such as Basic Calculator, Reverse Words in a String, Wildcard
Matching, Longest Valid Parentheses, Sudoku Solver, are already practice problems). What is missing is a long tail of 318
problems, a quarter of them warm-ups.

The highest new ones (not in the app today): String to Integer (atoi) (asked by all six big companies), First Bad Version,
Best Time to Buy and Sell Stock IV, Rotate String, Number of Recent Calls, Validate IP Address, Water and Jug Problem,
Valid Number, Number of Digit One, Guess the Word, Insert Delete GetRandom O(1) with Duplicates, Critical Connections in a Network,
Count of Smaller Numbers After Self, Palindrome Partitioning II, Exam Room, Minimum Cost to Reach Destination in Time.

## 2. Scoring (the formula, so it can be argued with)

For a problem `p` and each company `c`:

    company_score(p) = sum over c of  tier_weight(c) * frequency(c, p) / 100 * (1.25 if asked in the last six months else 1.0)

- `tier_weight`: **1.0** for Google, Amazon, Meta, Microsoft, Apple, Netflix; **0.5** for the other 39 (Uber, LinkedIn, Airbnb,
  Bloomberg, Adobe, Oracle, Salesforce, ByteDance, TikTok, Nvidia, Atlassian, Stripe, Databricks, Snowflake, Pinterest, Snap, Lyft,
  DoorDash, Dropbox, Intuit, PayPal, Cisco, VMware, Coinbase, Robinhood, Goldman Sachs, Tesla, Walmart Labs, Visa, Morgan Stanley, SAP,
  Samsung, X, Roblox, Instacart, Citadel, Two Sigma, Jane Street, Block). The list is a file; the owner can change it.
- Concept weight (importance of the idea), from LeetCode's topic tags, the largest tag of the problem:
  dynamic programming 1.0; graph, BFS, DFS, trees, binary search, two pointers, sliding window 0.9; heap, backtracking, BST 0.85;
  hash table, stack, monotonic stack, greedy, linked list, topological sort, memoization 0.8; shortest path 0.75; union find, trie,
  prefix sum, sweep line, monotonic queue 0.7; bit manipulation, design, recursion 0.6; string, matrix, sorting 0.55; array, segment
  tree, binary indexed tree, counting 0.5; math 0.45; simulation 0.4; geometry 0.2.

        score(p) = company_score(p) * (0.5 + 0.5 * concept_weight(p))

  So frequency leads, and a central concept lifts a problem by up to 2x relative to a peripheral one.

Tiers (thresholds are in the weights file):

| tier | rule | tag shown |
|---|---|---|
| **A** | asked by 4 or more of the six big companies, or score 2.5 or more | **MUST** |
| **B** | 3 of the six, or score 1.5 or more | **STRONG** |
| **C** | score 1.0 or more | not shown (kept in the data) |
| warm-up | easy, and tagged only array, string, hash table, math, sorting, counting, simulation, prefix sum, matrix | **WARM-UP** (never MUST) |

Warm-ups are demoted because they score high on frequency alone (Running Sum of 1d Array, Jewels and Stones): good for the first ten
minutes of a session, not what makes a candidate.

## 3. The tags (the vocabulary)

| group | tags | meaning |
|---|---|---|
| Priority | `MUST`, `STRONG`, `WARM-UP` | the tiers above |
| Evidence | `GOOGLE`, `AMAZON`, ... (up to 3 shown, the rest in the tooltip), `BIG-6 ×4`, `RECENT` | who asks it, how many of the big six, whether it was asked in the last six months |
| Concept | the pattern (D1..D18) and technique (existing ids), plus the LeetCode topic tags | what it practises, and where it sits on the pattern page |
| Source | `LISTS` (in the NeetCode lists) and `BEYOND` (outside them; the same word the BusTub page uses for extras) | |
| State | `IN APP` / `NEW` | whether the problem is already a practice problem (this exists in the app) or must be added |

A problem has one priority, any number of evidence tags, one pattern and one technique, and exactly one source.

## 4. Where it resides

```
tools/neetcode/must_solve.py            fetch the dataset, score, assign pattern and technique, write the file below
tools/neetcode/must_solve_weights.json  company set and tier weights, concept weights, tier thresholds, warm-up rule (reviewable)
content/dsa/must_solve.json             the result, committed (generated; one entry per problem)
content/dsa/practice.json               the NEW problems are appended here, so they get attempts, reviews and progress like the others
```

`must_solve.json` entry (all derived numbers, no raw lists):

```json
{ "slug": "string-to-integer-atoi", "tier": "A", "score": 4.32, "big6": 6, "companies": [["Netflix", 40.0], ["Amazon", 100.0], ["Microsoft", 71.4]],
  "recent": true, "warmup": false, "pattern": "Arrays & Hashing", "technique": "Arrays & Hashing:simulation" }
```

- **Stable ids.** A problem keeps its id `lc-<slug>`; progress is never moved. The `check-progress-safety` step passes, because nothing
  is removed.
- **Technique for a new problem** is chosen by the LeetCode tags the problem shares with the problems of each technique in the
  existing data (most overlap wins); a human reviews the generated assignments once (the 318 are listed in a report).
- **The data file records its date and the dataset's revision**; the raw CSVs are not committed (only derived numbers), and the
  dataset's provenance is written at the top of the file.
- **Refresh:** re-run the tool (a few minutes, 90 downloads); the diff shows which problems entered or left a tier.

## 5. How we show them

Everything here needs a mockup and the owner's approval first (decision 13); this is the intended shape.

1. **A badge on every problem row**, in every list (home, Problems, pattern pages, Practice, Review): `MUST` (accent), `STRONG`
   (outlined), `WARM-UP` (dim). Tooltip: "Asked at Amazon, Microsoft, Netflix and 3 other big companies · 13 companies · last six months".
2. **Problems view filters**, added to the existing cascading filters: Source (`Lists`, `Beyond the lists`), Priority
   (`Must`, `Strong`, `Warm-up`), and Company (a list of the companies in the data). The filter state is remembered like the others.
3. **DSA home card "Beyond the lists"**: a progress bar of Tier A solved (`0 / 331`), the next three problems, and a button into the
   filtered Problems view. Hidden until the NeetCode 150 goal passes 50%, so it does not compete with it (the owner decides).
4. **Pattern page, Practice tab**: a strip "Must solve beyond the lists" with that pattern's five highest, then the existing practice
   list sorted by priority.
5. **Plan and calendar** (later phase): an option "after the NeetCode 150, add Tier A problems" that appends them to the queue with
   the existing planner; off by default.
6. **A company view** (optional, last): "Asked at Google", the problems of that company in score order, with progress.

No new tracking system: a `NEW` problem becomes an ordinary practice problem (log it, review it, count it).

## 6. Phases

| phase | what | output | check |
|---|---|---|---|
| 0 | owner answers section 9 | thresholds, company set, warm-up policy | written in this file |
| 1 | tool, weights file, `must_solve.json`, loader and API fields (`priority`, `companies`, `recent`), the NEW problems appended to `practice.json` | data and API, no UI | loader and API tests; `anneal validate`; progress safety; a report of the technique assignments |
| 2 | mockup of the badge, filters, home card and pattern strip | an HTML mockup in docs/mockups | owner approves |
| 3 | build the badge, filters, home card and pattern strip | the UI | browser tests (filters narrow the list; badge tooltip; card progress) |
| 4 | plan integration and the company view | optional | tests |

## 7. Risks and how they are handled

- **Dataset provenance and freshness.** It is a public community dataset (derived from LeetCode's company tags) that changes
  quarterly. We keep derived scores only, record the date, and re-run on demand. If it disappears, the committed file still works.
- **Frequencies are relative per company** (100 is that company's top problem), so a small company's top problem scores as high as
  Google's. The tier weights and the recency factor compensate; the weights are a reviewable file.
- **Concept weights are my judgement.** They are in the weights file so they can be changed in one place; changing them re-ranks
  without touching code.
- **Overlap with the app's own practice list** (579 problems): the tool tags them (`MUST`/`STRONG`) and does not duplicate them.
- **The long tail of warm-ups** (80) would dilute "must solve": hence the `WARM-UP` tier.
- **Premium problems** (5 in Tier A/B): flagged `PREM` like the others, never required.
- **A new problem with no obvious technique** (about 2 in 318): left as `Other` until a human assigns it.

## 8. What is not part of this plan

Company-specific interview loops, system design, behavioural questions, and any change to how the NeetCode lists themselves are
unchanged. Problems outside LeetCode (other platforms) are out of scope.

## 9. Decisions needed from the owner (with recommendations)

1. **Company set and tiers.** Is the 6 + 39 split right? *Recommend:* yes, and add or remove companies you actually target.
2. **Thresholds.** Tier A = 4 of the big six or score 2.5. This gives 331 problems (198 already in the app, 133 new). *Recommend:* keep
   it; Tier B (310) is shown but not pushed.
3. **Warm-ups.** Demote the 80 easy trivia problems to `WARM-UP` (never `MUST`)? *Recommend:* yes.
4. **Where they live.** Append the 318 new problems to `practice.json` so they are tracked like the others? *Recommend:* yes; the
   alternative (a separate untracked list) cannot be logged or reviewed.
5. **Home card.** Show the "Beyond the lists" card from the start, or only after the NeetCode 150 reaches 50%? *Recommend:* after 50%.
6. **Order of work.** Build phase 1 (data and API, invisible) first, then the mockup? *Recommend:* yes.

## 10. A technique needs an implementation, not a name (owner's correction, 2026-10-10)

The Learn page must not name a technique it does not teach. A lesson is: when to use it (signals), a template that runs, its traps,
and problems. Names without that are removed from the page (they stay in the lesson files as a roadmap, not as content).

How the lessons are chosen and written, so the effort goes where interviews are:

1. **Priority of a technique** = the sum of the scores (section 2) of the problems that use it, from `must_solve.json`, plus 1 for
   every NeetCode-list problem that teaches it. The tool prints the ranking per topic; the lessons are written top down.
2. **Each lesson** has a Python template that is executed by `check_lessons.py` against a brute-force model on random inputs
   (as the ten written so far are), signals, pitfalls, and 2 to 4 verified problems. Variants share one lesson as tabs.
3. **Order of topics:** Backtracking, Greedy, Intervals, Trees, Heap, Stack, Sliding Window, Linked List, Binary Search,
   Bit Manipulation, Tries, Math & Geometry, Arrays & Hashing, Two Pointers (then more Graphs and DP).
4. **Size:** about 8 to 12 lessons per topic for the first pass (about 120 lessons), which covers the techniques that carry the
   MUST problems; the long tail stays a roadmap.
5. **Until a lesson exists**, a technique is not shown; its problems appear under its section instead.
