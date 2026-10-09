The hash join of stage 6 outputs only matching pairs. A **left** hash join also outputs every left tuple that found no partner, once, padded with NULLs on the right: exactly the rule of the left nested loop join (stage 5), now with a different way of finding partners. The padded row can happen for two reasons: the key was not in the table, or the key had a NULL.

## The task

In `src/execution/executors/hash_join_executor.rs`, `unmatched_output(&self, left: &Tuple) -> Option<Tuple>` (called by `next` for a left tuple with no match):
- for a **LEFT** join: `Some` tuple of the left values followed by a NULL of the right column's type for every right column (`values_of`, `nulls_for`), with the plan's output schema;
- otherwise (inner join): `None`.

(Stage 6's `next` already calls it for a missing key and for a NULL key.)

## Tests

- Unmatched left rows are padded with NULLs; matched ones are as in the inner join.
- A left row with a NULL key is output once, unmatched.
- The result equals the nested loop left join's (the two algorithms must agree).
- The padding has the types of the right columns (`integer_null varlen_null`).
- With an empty right side every left row is output (100 rows).
- RIGHT and FULL joins are refused with `NotImplemented`.

## Syntax and methods

```rust
use super::nested_loop_join_executor::{nulls_for, values_of};          // shared with the nested loop join
let mut values = values_of(left, self.left.output_schema());
values.extend(nulls_for(self.right.output_schema()));
```

## Notes

**Two algorithms, one answer.** The nested loop join (stage 5) is simple and obviously right; the hash join is fast and easy to get subtly wrong (a NULL key, a duplicate, the order of keys). The test `it_gives_the_same_rows_as_the_nested_loop_left_join` runs the same data through both and compares: **differential testing**, the cheapest way to test an optimised implementation against a slow reference.

**No match has two causes.** (1) The key is not in the table; (2) the key contains a NULL, so you never looked. Both lead to `unmatched_output`; for an inner join it returns nothing, for a left join the padded row.

**Same padding as before.** The two join executors share `values_of` and `nulls_for` (given, in the nested loop join's file) so the typed-NULL logic exists once.

**Right and full outer joins** need to remember which build-side tuples were matched and output the unmatched ones at the end; BusTub does not ask for them and `new` refuses them.

## In BusTub

`p3.14-hash-join.slt` has left joins such as `select * from temp_3 t3 left join temp_2 t2 on t3.colB = t2.colA;` with `+ensure:hash_join`, which the optimizer rule of module 3h makes true.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| copy-pasted NULL padding in each join executor | shared helpers `values_of` / `nulls_for` |
| comparing a hash join's output with a trusted one by eye | a test that runs both and compares sorted rows |
| `JoinType::LEFT` checked in two places | checked once, in the helper |

**Port rule:** share the padding code between joins; test the fast join against the slow one.

## Learn more
- [Differential testing](https://en.wikipedia.org/wiki/Differential_testing) · [PostgreSQL: outer joins](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM)

## Performance

Left padding costs nothing per matched row; each unmatched left row is one extra tuple. The probe side streams, so a left join of a huge left table with a small right table uses memory proportional to the right only.

**Measure it.** Left-join 100,000 left rows against right tables of 10 and 100,000 rows with 0% and 100% match.

## Hints

### Only the inner/left difference lives here

If your stage 6 tests pass and the left tests fail, the bug is in this function or in how `next` handles a NULL key: a NULL-key left row must still be passed to `unmatched_output`.

### Compare with the nested loop on every data set

Write a failing case as a SQL statement, run it with the hash join's hand-built plan and with `select ... join ... on` (a nested loop), and diff the two outputs.

### Types, again

`nulls_for(self.right.output_schema())` must use the *right child's* schema, not the plan's output schema (which includes the left columns).
