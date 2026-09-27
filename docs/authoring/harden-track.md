You are hardening the tests of problems in the anneal repo at /home/user/learn-rust (a Rust interview-prep platform).
Read /home/user/learn-rust/docs/HANDOFF.md §4, §5 and §6.1 first, then study how D1 was done: `tools/author/d1.py`
(every problem there is already hardened: compare `git show 485ab18^:tools/author/d1.py` style before vs now with
`git log -p --follow tools/author/d1.py | head -400` if useful) and a few folders under
`content/tracks/d1-arrays-hashing/problems/*/{tests,wrong}`.

YOUR TRACKS: {TRACKS}. Work them one at a time, in that order.

THE BAR, per ready problem:
- ≥ 5 visible tests and ≥ 8 hidden tests. Never remove or weaken an existing test; only add. The visible tests must let
  the user understand the problem before submitting: the main case, the empty/minimal input, and each rule that is easy
  to misread (ordering, duplicates, direction, ties, what to return when there is no answer).
  Keep them small and readable; heavy checks (random, scale, overflow traps) stay hidden.
  If the problem is a LeetCode question, include LeetCode's own examples among the visible tests (adapted to this
  problem's signature and conventions), and use its known tricky cases as a source for hidden ones.
- An edge-case checklist for its type: empty, single, duplicates, negatives, bounds/overflow (i32::MIN/MAX etc.), max
  size, Unicode for strings, plus the problem-specific traps.
- One randomized comparison against a brute-force reference written inside the hidden test, where a simple reference
  exists: `let mut rng = anneal_prelude::Rng::new(<unique seed>);` in a loop of ~200–400 small cases, using
  `check!(format!("<input desc>"), got, want)`. Rng API: `next_u64()`, `below(n) -> usize` (0..n), `int(lo, hi) -> i64`
  (inclusive), `vec::<T>(len, lo, hi) -> Vec<T>`, `bool()`, `pick(&slice) -> &T`, `shuffle(&mut slice)`,
  `string(len, alphabet) -> String`.
- One scale test sized so a wrong-complexity solution times out (the test run has a 15 s cap, debug build): usually
  n ≈ 10⁵–2·10⁵ so O(n²) ≈ 10¹⁰ ops. Put the work where a naive loop can't exit early. Keep the reference solution fast
  (well under 1 s): other agents share this 4-CPU machine. Where the statement's `constraints` are too small for this,
  raise them in the spec (and mention it in your report). Skip the scale test only where complexity isn't the point
  (e.g. many L-track "fix this borrow error" problems, O(1) functions).
- 1–3 `wrong` solutions: plausible but incorrect (the quadratic version, the classic off-by-one, the misread statement,
  for fix-mode problems a plausible wrong fix that still obeys the problem's rules). `anneal verify` fails if any wrong
  solution compiles and passes Submit, or fails to compile. If one passes, a test is missing: add a test that catches
  it rather than dropping the wrong solution (unless the "wrong" solution is actually correct).
- Randomized/scale tests don't make sense for every problem (e.g. a fix-this lifetime annotation); use judgement, but
  still meet the 3/8 counts and add wrong solutions.

HOW (important):
- `tools/author/<track>.py` is the source of truth for each track. Edit the spec there, then regenerate with
  `cd /home/user/learn-rust/tools/author && python3 <track>.py`. Add hidden items as `T(name, input_desc, call,
  expected)` and free-form test code as a plain string item in the `hidden` list (see d1.py). Add `wrong=dict(name="""
  code """)` to each problem dict. Never hand-edit generated content folders.
- EXCEPTIONS: do NOT touch `content/tracks/d9-graphs/problems/network-delay-time` or
  `content/tracks/l2-borrowing/problems/two-mutable-borrows-of-self` (hand-written, pinned by runner tests; the lead
  handles them).
- Verify with `cd /home/user/learn-rust && cargo run -q -p anneal-cli -- verify <code> --jobs 2 2>&1 | grep -v "^ok" | sed 's/\x1b\[[0-9;]*m//g'`
  and fix every failure until it says 0 failed. To run one problem: `cargo run -q -p anneal-cli -- run <problem-id>
  --solution --submit --no-clippy` or `--code <file> --submit --no-clippy`.
- Also run `cargo run -q -p anneal-cli -- validate | tail -1` (must say 0 issues).
- Pitfalls found on D1: build big inputs on the heap (`vec![x; n]`, never `[x; n]` or `extend([x; n])` for large n):
  a big stack array aborts the test binary and every later test shows "TIMED OUT". `Rng` calls can't nest
  (`rng.vec(rng.below(n), ..)` is E0499; bind the length first). `rng.pick(&strs)` passed to a `&str` parameter needs
  `*`. `check!` takes `got` and `expected` by value, so clone anything still borrowed. Test names must not equal a
  function they call. Double-check every hand-computed expected value (compute it with python3 when unsure). Python
  string escaping in the spec is easy to get wrong; look at the generated .rs after regenerating.
- Don't run prettier or cargo fmt. Match the surrounding style. Don't touch crates/, docs/, author.py, other tracks,
  or any file outside your tracks' `tools/author/<track>.py` and `content/tracks/<track-folder>/`.
- NEVER kill processes with `pkill -f` / `killall` (you'd kill other agents' work or your own shell).

COMMITS (other agents share this same git checkout, on branch master):
- After a track verifies with 0 failed, commit ONLY your paths, then push:
    cd /home/user/learn-rust && git add tools/author/<track>.py content/tracks/<track-folder> && \
    git commit -q -m "<CODE> test hardening: <one line summary>" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01VjzPuKbSra7ibnx8sphC8G" -- tools/author/<track>.py content/tracks/<track-folder> && \
    git push origin master
  If git reports `index.lock` exists, wait a few seconds and retry. If the push is rejected, run
  `git pull --rebase origin master` and push again. Never force-push, never amend, never commit other paths.

REPORT at the end, per track: problems changed, constraints you raised, anything you could not bring to the bar and
why, notable real gaps the wrong solutions exposed, and the final verify line.
