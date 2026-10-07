# Practice tracks

Handwritten problems per NeetCode pattern (docs/DSA.md, decision 23). Python first, then Rust. Not part of spaced
repetition. A problem opens when any of its `unlocked_by` DSA problems has been logged (any grade); one marked
`warmup = true` also opens while one of them is among the next three in the plan.

## Layout

```text
content/tracks/p1-graphs-practice/
  track.toml                  code "P1", section "P", pattern = "Graphs"
  problems/<slug>/
    problem.toml              language = "python", unlocked_by = ["lc-course-schedule"], warmup, hints, solution notes
    statement.md              the first paragraph is the card's blurb
    starter.py  solution.py
    tests/visible.py          at least 5 tests;  tests/hidden.py at least 8
    wrong/<name>.py           at least one plausible wrong solution the tests must reject
```

Tests are `def test_<name>():` functions. Use `from anneal_prelude import check, ensure`:
`check("call as text", got, expected)` shows input, expected and got on a failure; `ensure(cond, "message")` is for
answers that aren't unique (any valid order). `from solution import <function>` gives the user's code.

`cargo run -q -p anneal-cli -- verify P1` runs the solution (must pass everything), the starter (must fail), and every
wrong solution (must fail a test). It needs `python3` on the host; the app runs the same harness in the Docker sandbox.

## Checking the editor

`tools/ui-keys.mjs` types into the real editor in headless Chrome. Use a throwaway database so your settings (Vim on or
off) and progress are untouched:

```sh
docker exec learn-rust-postgres-1 psql -U anneal -c "CREATE DATABASE anneal_ui"
ANNEAL_DATABASE_URL=postgres://anneal:anneal@127.0.0.1:5435/anneal_ui ANNEAL_ADDR=127.0.0.1:8799 ANNEAL_SANDBOX=host \
  cargo run -q -p anneal-api &
node tools/ui-keys.mjs http://127.0.0.1:8799/p/<a practice problem id> tools/ui-python-editor.json      # Vim off
# turn Vim on (PUT /api/settings/editor with "vim": true), then:
node tools/ui-keys.mjs http://127.0.0.1:8799/p/<id> tools/ui-python-editor-vim.json
node tools/ui-keys.mjs http://127.0.0.1:8799/p/<id> tools/ui-python-flow.json                            # Vim on
```

The scripts assume the problem's editor starts as its starter (`sorted-pair-sum` in the API test fixtures does).
