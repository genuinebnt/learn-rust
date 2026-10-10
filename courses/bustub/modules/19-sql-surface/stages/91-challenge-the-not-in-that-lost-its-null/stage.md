A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`not_in` in `src/execution/not_in.rs` evaluates `x NOT IN (list)` for a value and a list that may contain NULLs. A well-meant simplification, "NULLs can never match, so drop them first", makes it return TRUE where SQL says unknown. Find the bug and fix it.

## Why

This is the most common wrong answer a hand-written NOT IN produces, and it is wrong in the direction that looks right: the NULL cannot equal anything, so ignoring it seems harmless. What it throws away is the *possibility* that the value equals something unknown, which is exactly what makes SQL return no rows. A query that is wrong only when a list happens to contain a NULL is the kind that works for years.

## The contract

- `not_in(x, list)` is TRUE if `x` is not NULL, differs from every item and the list has no NULL (or is empty); FALSE if `x` equals some item; NULL otherwise.
- `x` NULL with an empty list is TRUE: there is nothing it could equal.

## Invariants

These must hold after every step, whatever the input:

- `not_in` is never TRUE for a non-empty list containing a NULL.
- `not_in(x, list)` is the three-valued negation of `x IN list`.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- Removing a non-NULL item from a list can only move the answer towards TRUE.
- Adding a NULL to any list never makes the answer TRUE.

## Examples

Worked cases (the tests include them):

```text
x = 3, list [1, 2]: TRUE
x = 3, list [1, NULL]: unknown (NULL)
x = 1, list [1, NULL]: FALSE
```

## What the tests check

- The textbook cases.
- A NULL in the list.
- A NULL on the left.
- The empty list.
- A property against the definition.

## Done when

All the `s3i_c2` tests pass, and you can say in one sentence what the bug was.
