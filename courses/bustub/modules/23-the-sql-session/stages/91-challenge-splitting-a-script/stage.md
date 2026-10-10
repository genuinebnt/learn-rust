A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`split_statements` in `src/sql/split.rs`: split a script into its statements at the semicolons that really end one, without a full parser: skip over single-quoted strings (a doubled quote is a quote), double-quoted identifiers, `--` comments to the end of the line and `/* ... */` comments. Each statement comes back trimmed, without its semicolon; empty statements are dropped.

## Why

Every shell, migration tool and driver has to do this before a single statement reaches a session, and the naive `text.split(';')` breaks on the first `insert into t values ('a;b')`. It is also a small state machine that is easy to get almost right: the interesting bugs are an unterminated string at the end, a quote inside a comment, and a doubled quote.

## The contract

- Normal text ends a statement at `;`.
- A `'` starts a string that ends at the next `'` not followed by another `'`; `;` inside is ordinary.
- A `"` starts a quoted identifier that ends at the next `"` (`""` is a quote).
- `--` starts a comment that ends at the end of the line; `/*` one that ends at `*/` (no nesting). A `;` inside a comment is ordinary, and quotes inside a comment do not start strings.
- An unterminated string or comment runs to the end of the text: it is the last statement as it stands.
- Each returned statement is trimmed of whitespace; statements that are empty after trimming are dropped.

## Invariants

These must hold after every step, whatever the input:

- Joining the result with `;` and splitting again gives the same list.
- No returned statement is empty.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- A script without special characters equals `text.split(';')` trimmed, empties dropped.
- Appending a statement appends exactly one element.

## Examples

Worked cases (the tests include them):

```text
`select 1; select 2;` -> [`select 1`, `select 2`]
`insert into t values ('a;b'); select 1` -> two statements
`select 1 -- a; b` -> one
```

## What the tests check

- Plain splitting and empties.
- Strings and quoted identifiers.
- Comments.
- Unterminated input.
- A property against a model.

## Done when

All the `s4e_c2` tests pass.
