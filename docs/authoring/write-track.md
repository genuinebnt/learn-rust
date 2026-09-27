You are writing a new DSA track for anneal, a personal Rust interview-prep platform at /home/user/learn-rust.

READ FIRST: docs/HANDOFF.md §4 (owner's rules), §5 (content authoring) and §6.1 (the test bar and how it was met);
docs/CURRICULUM.md §1 (bands, stages, problem types, time budgets) and YOUR track's section in §4, which lists every
problem in order. Then study tools/author/author.py and two finished specs: tools/author/d1.py (write-mode and fix-mode
problems, hidden free-form tests, `wrong=dict(...)`) and tools/author/d5.py (a shared helper constant included in
starter and solution). Look at a few generated folders under content/tracks/d1-arrays-hashing/problems/. Also read the
validator in crates/content/src/catalog.rs (`check_problem`, `check_track`) so `validate` passes first time.

YOUR TRACK: {TRACK}

WHAT TO PRODUCE
- `tools/author/{SPEC}` generating `content/tracks/{FOLDER}` via `write_track(...)`, with track.toml
  code/name/section "D"/tier "core"/order {ORDER}/summary and the stages listed in CURRICULUM (slug, name, band).
- Every problem listed for your track in CURRICULUM, in that order, status ready. Stages climb easy → medium → hard, and
  inside a stage problems climb from easiest to hardest. The owner wants the progression gradual and not frustrating:
  each stage opens with the smallest version of its idea, statements are short and concrete, hints genuinely help
  (1–3: approach → Rust → edge case), notes explain the idea and give time/space.
- Idiomatic Rust signatures: slices in, owned out; `Option` instead of -1 sentinels; `usize` for counts/indices; `u64`/
  `i64` where sums can overflow. Keep LeetCode's shapes where the curriculum says so (e.g. D6 basics use LeetCode's
  `Option<Rc<RefCell<TreeNode>>>`; give a shared helper constant with the node type plus builders/readers used by
  starter, solution and tests, like D5's LIST).
- Write statements in your own words (don't copy LeetCode's text); a LeetCode problem keeps its well-known title.
- Fix-mode ("Fix:") problems: a broken starter (compile error or wrong behaviour), a solution, and `rules` (forbidden
  methods/types, max changed lines) as in d1.py; the starter must fail, the solution must pass without breaking a rule.
- Fill `teaches`, `tags`, `examples`, `constraints`, `follow_up`, `related` (track codes like "S4", "D9") like d1.py.

THE TEST BAR (every problem)
- ≥ 5 visible tests that explain the problem before a Submit: the main case, the empty/minimal input, and each rule that
  is easy to misread (order, duplicates, ties, no-answer value). For a LeetCode question include LeetCode's own examples
  (adapted to the signature).
- ≥ 8 hidden tests: the edge checklist (empty, single, duplicates, negatives, bounds/overflow, max size, Unicode for
  strings) plus the problem's traps and LeetCode's known tricky cases.
- A seeded randomized comparison against a brute force written inside the hidden test, where a simple reference exists:
  `let mut rng = anneal_prelude::Rng::new(<unique seed>);` (API: `below(n)`, `int(lo, hi)` inclusive, `vec::<T>(len, lo,
  hi)`, `bool()`, `pick(&slice)`, `shuffle(&mut slice)`, `string(len, alphabet)`), ~200–400 small cases, with
  `check!(format!("<input>"), got, want)`. Use seeds {SEEDS}.
- A scale test sized so the wrong complexity times out (15 s cap, debug build) while the reference stays well under
  1 s; skip only where complexity isn't the point. Put big inputs on the heap (`vec![..]`, never large `[x; n]`).
- 1–3 `wrong` solutions (plausible: the naive complexity, the classic bug, the misread statement). `verify` fails if a
  wrong solution compiles and passes; then a test is missing — add one.
- Exponential problems (backtracking) have no "scale" in the usual sense: size the largest test so a solution without
  the key pruning/memo times out, if there is such a solution; otherwise skip the scale test.

CHECKING
- Regenerate: `cd /home/user/learn-rust/tools/author && python3 {SPEC}`.
- `cd /home/user/learn-rust && cargo run -q -p anneal-cli -- validate | tail -3` must report 0 issues.
- `cargo run -q -p anneal-cli -- verify {CODE} --jobs 1 2>&1 | grep -v "^ok" | sed 's/\x1b\[[0-9;]*m//g'` must say
  0 failed. Use --jobs 1: other agents share this 4-CPU machine. If a reference solution times out, re-run that problem
  alone (`cargo run -q -p anneal-cli -- run <id> --solution --submit --no-clippy`) before deciding it's too slow; make it
  comfortably fast either way.
- Pitfalls: `Rng` calls can't nest (bind the length first); `rng.pick(&strs)` into a `&str` param needs `*`; `check!`
  takes values, so clone what's still borrowed; a test name must not equal a function it calls; double-check every
  hand-computed expected value (compute with python3); look at the generated .rs after regenerating, Python escaping is
  easy to get wrong. Don't run prettier/cargo fmt. Match d1.py's style.
- NEVER use `pkill -f`/`killall`. Touch only `tools/author/{SPEC}` and `content/tracks/{FOLDER}/`.

COMMITS (other agents share this checkout, branch master; commit often so work survives a container restart)
- After each stage verifies with 0 failed (verify runs the whole track; it's fine that later stages don't exist yet),
  commit only your paths and push:
    cd /home/user/learn-rust && git add tools/author/{SPEC} content/tracks/{FOLDER} && \
    git commit -q -m "{CODE}: <stage name> (<n> problems)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01VjzPuKbSra7ibnx8sphC8G" -- tools/author/{SPEC} content/tracks/{FOLDER} && \
    git push origin master
  On `index.lock`, wait and retry. On a rejected push, `git pull --rebase origin master` then push. Never force-push or
  amend, never commit other paths.

REPORT at the end: problems written per stage, anything you left out or changed from the curriculum list and why,
constraints you chose that differ from LeetCode's, and the final verify and validate lines.

COMPANY TAGS (added later by the owner)
- Give each problem dict `companies=[...]`: the companies known to ask it, names ONLY from `COMPANIES` in
  crates/content/src/model.rs (validate rejects others). Priority: FAANG + Microsoft, then other big tech; database
  companies and Rust shops only where you have a real reason (their interviews are less LeetCode-driven). Several per
  problem is normal for classic LeetCode questions; list FAANG first. Don't invent associations: Rust-specific and
  fix-this problems usually get none.
