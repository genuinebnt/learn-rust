A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`src/sql/mini_parse.rs` is a precedence-climbing parser for `+ - * /` over integers. It gets `2 + 3 * 4` right, and `10 - 4 - 3` wrong. Find the bug and fix it.

## Why

Left associativity is one `+ 1` in a precedence climber, and forgetting it produces a parser that passes every test with a single operator and silently mis-evaluates every long chain of subtractions and divisions. The tree is the output of the front end; a wrong shape here is a wrong query result there.

## The contract

- `parse_and_eval(text)` parses and evaluates with integer arithmetic (division truncates toward zero; `None` on a syntax error or division by zero).
- `*` and `/` bind tighter than `+` and `-`; all four are **left**-associative; parentheses group.

## Invariants

These must hold after every step, whatever the input:

- The result equals evaluating the expression with the usual rules of arithmetic.
- The parser consumes the whole input or fails.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- Wrapping any left chain in parentheses from the left does not change the value.
- `a - b - c == (a - b) - c` and `a / b / c == (a / b) / c`.
- Adding spaces never changes the value.

## Examples

Worked cases (the tests include them):

```text
10 - 4 - 3 = 3
100 / 10 / 5 = 2
2 + 3 * 4 = 14
2 * 3 - 4 - 1 = 1
```

## What the tests check

- Chains of each operator.
- Mixed precedence.
- A property against a reference evaluator.

## Done when

All the `s3d_c3` tests pass, and you can say in one sentence what the bug was.
