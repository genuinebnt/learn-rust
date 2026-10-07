# anneal · spaced repetition

The owner called this "the most important part of the DSA track". This doc records the algorithm, the routine it's
built around, and the measurements behind every default. The code is `crates/api/src/reviews.rs` (pure functions
with tests) and `store::record_review`.

## The owner's routine (2026-10-07)

- **A new problem every day but Sunday** (Mon–Sat, about 6 a week).
- **Sunday reviews the week's new problems**, plus a few older ones.
- **Older problems come back one a day** on weekdays, and a little practice on Saturday ("practice on Saturday too,
  but don't overwhelm me").
- **Target:** the NeetCode 150 without the 7 Premium problems (143 problems), plus a few from the 250, by the end of
  March 2027. **It's an ideal, not a deadline**: nothing in the scheduler depends on it. It only drives the pace
  display, which shows a projected finish date from the actual pace and never nags.
- Reviews are **quick recalls** (state the idea, write the skeleton, about 6 minutes), not full re-solves, except
  when a recall fails.

## The algorithm: FSRS-6

The memory model is **FSRS-6**, from the open-spaced-repetition project's official `fsrs` crate (BSD-3, v6.6): the
scheduler modern Anki uses, fitted to hundreds of millions of real reviews, replacing the older SM-2. It's much better
founded than the fixed ladder this replaced (3, 7, 21, 60, 180 days).

Each problem has a **stability** (days until recall drops to 90 %) and a **difficulty**. **Retrievability** is the
probability of recalling it now. A review is graded, and the model updates both and picks the next interval for the
**desired retention** (default 85 %):

| Grade | Meaning | In the DSA log |
|---|---|---|
| again | couldn't, or had to look | ✗ couldn't yet |
| hard | got there with real struggle or hints | ½ with help |
| good | solved on my own | ✓ on my own |
| easy | instant, whole approach recalled | (fourth button) |

The Rust workspace grades itself: a solve with no hints is *good*, one that used hints is *hard*.

Defaults are FSRS's trained parameters. The crate includes an optimizer that can fit them to the owner's own history
once there are a few hundred reviews; that's a later step, not needed to start.

What it produces (85 % retention, first solve): again 0.4 d, hard 2.5 d, good 4.4 d, easy 15.8 d. A problem recalled
every time is reviewed at about 4 d, 31 d, 173 d, then 2 years. Failing a well-known one cuts the interval to a quarter
or less. Reviewing late still works and earns more stability, which is why a backlog is safe.

## Capacity-aware scheduling (what FSRS alone doesn't do)

FSRS alone would ask for about 3 reviews a day at one new problem a day. That doesn't fit the routine, so on top of it:

1. **Each weekday has a capacity** (`settings.srs.capacity`, default Mon–Fri 1, Sat 3, Sun 12). Due dates snap to the
   day with room closest to the ideal one: a little early costs less than late, and a day's cost rises with the
   reviews already planned for it, steeply over capacity.
2. **A problem's first review is held on the consolidation day** (Sunday), so the week's problems are reviewed
   together. It costs nothing in recall (87.8 % vs 87.3 % without it in the simulations).
3. **The day's plan** (`reviews::pick`) is the problems due, most forgotten first, up to that day's capacity. The rest
   stay overdue and go first next time.
4. **Readiness** (`reviews::credit`) is the chance of still recalling a solved problem, never below a quarter of the
   credit. It replaces the old "10 % off per overdue week".

## Measured, not guessed

A Monte Carlo simulation (a virtual learner who recalls with the model's own probability, 12 seeds) of the routine,
143 problems, 85 % retention, 7 Oct 2026 to 31 Mar 2027:

| Plan | Reviews/week | Busiest day | Recall of the 143 on 31 Mar |
|---|---|---|---|
| FSRS with no limit | 18 (2.5–4.4 a day average) | up to 28 on one day | 92 % |
| Sunday only, cap 18 | 16 | 18 | 87 % |
| Mon–Sat 1 + Sunday 14 | 17 | 14 | 88.5 % |
| **Mon–Fri 1, Sat 3, Sun 12 (default)** | **17** | **12** | **88.9 %** |
| Mon–Fri 1, Sat 3, Sun 8 | 14.5 | 8 | 86 % |

- **Retention** barely matters once capacity binds (80 / 85 / 90 % all give 82–83 % at a cap of 2 a day); 85 % is the
  default because it needs the fewest reviews that still hold the result.
- **New problems:** Mon–Sat finishes the 143 around 22 March, about 9 days early. Mon–Fri only would miss March.
  All 151 slots (143 + 8 from the 250) would miss it by a day, so plan on about 5 from the 250 as a bonus.
- **Missing days doesn't pile up.** Each problem is one item however late, so the queue is bounded by the problems
  learned. Over 12 runs, the most reviews ever waiting was 44, even after a four-week break, and recall on 31 March
  stayed at 89 % in every case. What a missed day costs is *new problems started*: 134 of 143 by 31 March with 10 %
  of days missed, 113 with 25 %. Pausing new problems when the backlog grows didn't help recall (89.9 % vs 89.2 %) and
  cost 7 problems, so there's no automatic pause.

The simulations are throwaway probes; the same logic is pinned in `reviews.rs` tests, including a seeded simulated
learner that must recall about as often as promised (78–92 % at review) and never exceed a day's capacity.

## Data

`reviews` (one row per problem): `stability`, `difficulty`, `last_review`, `last_grade`, `reps`, `lapses`, `due_at`,
and `history` (one entry per review: grade, recall before, new stability and difficulty, the ideal interval and the
due date). `step` stays as a coarse 0–4 level from stability so older screens work. Migration `0008_fsrs.sql` converts
rows from the ladder: stability is the interval they had been given, difficulty the model's middle.

## Settings

`GET /api/settings` returns `srs`; `PUT /api/settings/srs` saves it: `retention` (0.70–0.97), `capacity` per weekday
(0–100), `consolidate_on` (a weekday or null), `new_days` (the weekdays a new problem is solved on; the others are
practice or rest days), `new_per_day` (new problems on a solve day), `target_date` (a soft goal).

**Pace** (`reviews::pace`): from the problems left, today, the target date and the solve days it returns the solve days
left, the problems needed per solve day (rounded up) and per week, the finish date at the chosen pace, and the days
ahead of or behind the target. With the default routine, 143 problems from 7 Oct 2026 need 1 a solve day and finish on
22 March 2027, 9 days early; one a day on Mon, Wed and Fri only needs 2 a day and misses March.

## Still to build

- The daily plan endpoint and screens: today's reviews (`pick`), the next new problem, the pace display (projected
  finish from the last two weeks' rate), and a forecast of the coming weeks against capacity. Mock up first.
- A fourth log button (*easy*) and quick-recall review mode on the DSA problem page.
- Later: fit FSRS's parameters to the owner's own reviews with the crate's optimizer.
