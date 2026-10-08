# Course standards: what every stage and page must follow

These are the owner's decisions, in their own words where it matters. They were given over several sessions because earlier work drifted from
them. **Read this before changing anything under `courses/` or the Courses pages (`web/src/pages/Course*`)**, and run `anneal course lint`
(it also runs in CI). Do not rely on memory of "what CodeCrafters looks like": fetch or ask when a site is named as the model.

## The decisions

1. **A learning track as well as a project track.** The goal is to teach an idea and have the learner use it to solve the exercise. Every
   stage names what it teaches (`learn = [...]` in `stage.toml`), links a concept article (`concepts = [...]`, files in `courses/<id>/concepts/`),
   and the exercise uses that concept. The concept comes first on the page ("Read first").
2. **Stage size.** *"not too small but self contained exercises"*, *"i am not looking for one or two line change exercise"*, *"6 - 10 exercises
   is sweetspot but not a hard requirement"*. A stage is a self-contained exercise: tens of lines and a design decision, passable on its own.
   Group tiny pieces; split a chapter. About 6 to 10 stages per module; the last stage of a module is BusTub's own test, ported (kind `boss`).
3. **Tests.** *"have atleast 5 test cases"* and *"ensure the texts dont clutter the challenges with too many unnecessary tests"*. Every
   non-boss stage has at least 5 tests, each checking a distinct behaviour (no padding, no near-duplicates). The stage text summarises the key
   behaviours: at most 4 bullets per `### Tests` block and 8 per stage; the learner sees every test by name in the Last run tab.
4. **Performance.** *"have performance sections"*. Every non-boss stage has a `## Performance` section: the cost model (complexity, syscalls,
   allocations, lock hold times), what the obvious version costs, what to measure and how (`strace -c`, a timing test, counters). Claims must be
   things you can check; hedge ("typically") instead of inventing numbers.
5. **Hints at BusTub's level.** *"the hints and the content should not be trivial or basic … bustub is a serious exercise"*. `## Hints` has at
   least 2 `###` hints per stage, deepest last: the design choice, then the trap, then the invariant to check. Never a restatement of the task.
6. **Pages.** The course overview is sections (modules) of stage rows with a difficulty mark, like CodeCrafters' course page; each stage is its own
   page with tabs (Instructions, Hints, Solution, Concepts, Last run); a concept is its own page. Everything uses anneal's design (the /rust
   catalog's styles and components), with callouts, highlighted code and colour-coded C/C++ vs Rust tables. Mockups come before big UI changes
   (CLAUDE.md) and are built from the real reference, not from memory.
7. **Mirror BusTub; show the C/C++ way** (tables, "Port rule" callouts), link CMU lectures and verified resources, keep the learner free to
   solve it their own way (only the tests must pass), test every stage (fail before, pass after) and ship module by module.

## How these are enforced

- `anneal course lint` (content only, needs no reference): for every non-boss stage of a *published* module (`published_modules` in `course.toml`;
  `--all` checks the rest): `learn` has 2 or more entries, at least one concept exists, a Performance section exists, at least 2 hints, and the
  `### Tests` text stays short (at most 4 bullets per block, 8 per stage). CI runs it.
- `anneal course verify` also fails a non-boss stage with fewer than 5 tests.
- A module is added to `published_modules` only when lint and verify are clean for it.
