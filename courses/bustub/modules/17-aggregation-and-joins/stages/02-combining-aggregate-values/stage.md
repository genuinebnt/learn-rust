An aggregate is a running value updated once per row: `count(*)` starts at 0 and adds 1; `sum(x)` starts at "nothing yet" and adds `x`; `min` and `max` keep the smaller or larger. The rule that gives SQL its character: **NULL inputs are ignored**, and an aggregate that has seen only NULLs is NULL. This stage writes the *combine* function: given the running values of a group and one input row's values, produce the new running values.

## The task

In `src/execution/executors/aggregation_executor.rs`, `SimpleAggregationHashTable::combine_aggregate_values(&self, result: &mut AggregateValue, input: &AggregateValue) -> Result<()>`. For each aggregate `i`, with type `self.agg_types[i]`, running value `result.aggregates[i]` and input `input.aggregates[i]`:
- `CountStarAggregate`: add 1 (every row counts, NULLs included);
- for the others: if the input is NULL, change nothing;
- `CountAggregate`: the running value becomes 1 if it is NULL ("nothing seen yet"), else + 1;
- `SumAggregate`: the input if the running value is NULL, else the running value `add` the input;
- `MinAggregate` / `MaxAggregate`: the input if the running value is NULL, else `min` / `max` of the two.

(The initial values, `count(*)` = 0 and everything else NULL, are given in `generate_initial_aggregate_value`.)

## Tests

- The initial values, and each of the five aggregates over a few values (`5, -2, 9` gives count 3, sum 12, min -2, max 9).
- NULL inputs are ignored by everything but `count(*)`.
- A group of only NULLs keeps NULL aggregates (not 0).
- The first value seeds the running value (`max` of a single negative number is that number).
- A `sum` that overflows is an `OutOfRange` error.
- `insert_combine` keeps one running value per group key.

## Syntax and methods

```rust
for (i, agg_type) in self.agg_types.iter().enumerate() {
    let (running, x) = (&result.aggregates[i], &input.aggregates[i]);
    result.aggregates[i] = match agg_type { .. };       // build the new value, then store it
}
running.add(&Value::integer(1))?                        // Value arithmetic, checked (module 3a)
running.min(x)?  running.max(x)?
x.is_null()  running.is_null()
```

## Notes

**One rule for four aggregates.** Apart from `count(*)`, an aggregate does nothing for a NULL input and, on the first non-NULL input, simply adopts it (count adopts 1). After that it combines. Writing `if x.is_null() { skip }` once, before the `match`, keeps the four arms short.

**"Nothing seen yet" is NULL.** That is why `sum` of no rows (or of only NULLs) is NULL and `min` of an empty table is NULL, in standard SQL. BusTub's `count(x)` follows the same rule through its initial value: over an empty table `count(v1)` is NULL here (`integer_null` in `p3.07-simple-agg.slt`), where standard SQL says 0. The tests of this course follow BusTub's.

**Overflow is an error.** `Value::add` is the checked arithmetic of module 3a; a `sum` that does not fit an INTEGER is an error for the query, not a silent wrap.

**The table is given.** `insert_combine` (which finds or creates the group and calls your function) and the key/value types are written; `combine` is the heart.

## In BusTub

`aggregation_executor.h`, `SimpleAggregationHashTable::CombineAggregateValues` ("`for (uint32_t i = 0; i < agg_exprs_.size(); i++) { switch (agg_types_[i]) { case AggregationType::CountStarAggregate: ... } } UNIMPLEMENTED("TODO(P3): Add implementation.");`") and `GenerateInitialAggregateValue` (count(*) starts at `GetIntegerValue(0)`, the rest at `GetNullValueByType(TypeId::INTEGER)`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `result->aggregates_[i] = result->aggregates_[i].Add(input.aggregates_[i])` | `result.aggregates[i] = running.add(x)?` |
| a `switch` with a `break` per case | a `match` that evaluates to the new value |
| `if (input.aggregates_[i].IsNull()) { continue; }` | `_ if x.is_null() => continue,` as a match guard |
| overflow in `Add` is UB or an exception, depending on the type | `Result<Value>`: an `OutOfRange` error |

**Port rule:** a state-update `switch` becomes a `match` that returns the new state.

## Learn more
- [`match` guards](https://doc.rust-lang.org/book/ch18-03-pattern-syntax.html#extra-conditionals-with-match-guards) · PostgreSQL [aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html) · [`i32::checked_add`](https://doc.rust-lang.org/std/primitive.i32.html#method.checked_add)

## Performance

Combine runs once per input row per aggregate: a few `Value` matches and one allocation for a string min/max. For a billion-row table that is the inner loop of the query. Real engines specialise it per type (`sum_i32`) and update whole columns at once.

**Measure it.** Fold a million rows into `count(*), sum, min, max` and time it; then try with all inputs NULL (the early `continue`).

## Hints

### Compute the new value before storing it

`result.aggregates[i] = match ... { }` reads `running` (a borrow of `result`) and then writes `result`. Compute into a new `Value` first; the borrow checker will tell you if you try to do both at once.

### `count(*)` ignores the input

Its input is the constant `1` (the planner gives `count(*)` the expression `1`), never NULL; the rule "NULLs are ignored" does not apply to it, so keep it out of the NULL check.

### Test the seeds

`max` of `[-7]` must be `-7`. A running value initialised to 0 and combined with `max` would answer 0; that is why the initial value is NULL and the first input *replaces* it.
