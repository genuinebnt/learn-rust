A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`CoalesceExpression` in `src/execution/expressions/coalesce_expression.rs`: an expression with one or more children that returns the first child value that is not NULL, **evaluating each child at most once and stopping at the first non-NULL**. The binder's rewrite of COALESCE into a CASE evaluates an argument twice (once to ask whether it is NULL, once to use it); this node does not.

## Why

For a column reference the second evaluation costs nothing. For an expensive argument (a function, a subquery, a user-defined function with a side effect) it doubles the work, and for a volatile one (`random()`, `nextval()`) it gives two different answers inside one expression. A dedicated node is also what PostgreSQL has, for the same reasons.

## The contract

- `new(args)` needs at least one argument and one type shared by all (a bare NULL constant adopts it): else `MismatchType`.
- `evaluate` and `evaluate_join` return the first non-NULL value among the children, evaluated in order, each at most once; NULL of the result type if all are NULL.
- `return_type` is the shared type; `children` returns the arguments in order.

## Invariants

These must hold after every step, whatever the input:

- No child is evaluated after a non-NULL one has been found.
- No child is evaluated more than once per call.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- `coalesce(a)` is `a`.
- `coalesce(NULL, NULL)` is NULL of the shared type.
- The result of `coalesce(a, b)` is `a` whenever `a` is not NULL, whatever `b` would have done (even an error).

## Examples

Worked cases (the tests include them):

```text
children evaluate to [NULL, 7, 9]: result 7, the third child is never evaluated
children [3, error]: result 3, the error is never reached
```

## What the tests check

- First non-NULL wins.
- Later children are not evaluated.
- Each child once.
- Types and arity.

## Done when

All the `s3i_c6` tests pass.
