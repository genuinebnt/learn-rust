A nested loop join compares every left tuple with every right tuple. When the predicate is an **equality** (`a.x = b.y`), nearly all of those comparisons are wasted: only tuples with the same key can match. A **hash join** groups the right tuples by key once (the **build** phase) and then, for each left tuple, looks up only the right tuples with its key (the **probe** phase): `|L| + |R|` instead of `|L| × |R|`.

BusTub's `HashJoinPlanNode` carries the two lists of key expressions (`left_key_expressions`, `right_key_expressions`); the optimizer rule that turns an equality nested loop join into one is yours in module 3h. This stage writes the executor, tested with plans built by hand.

> [!CHECK] Two rows have NULL in their join columns, and the join condition is `a.x = b.y`. What does the condition evaluate to? Does the hash join match them? What does an INNER join output for the left row, and what does a LEFT join?
> ||The condition is NULL, not true, so they never match; the hash join must therefore never put a NULL key in the table or probe with one. An INNER join drops the left row; a LEFT join outputs it once with NULLs for the right columns.||
>
> - What does `join_key` return for a key that contains a NULL?
> - What does a probe with no match do for each join type?
> - Which rows of the right side can never be found?

## The task

In `src/execution/executors/hash_join_executor.rs` (the struct, `new`, the `TupleStream`s, `unmatched_output` for stage 7 are given; the key type is stage 1's `AggregateKey`):
- `join_key(exprs, tuple, schema) -> Result<Option<AggregateKey>>`: evaluate each key expression on the tuple; if **any** value is NULL the result is `None` (a NULL key matches nothing); otherwise `Some(key)`;
- `init`: initialise both children; clear the table and the pending output; **build**: for every right tuple whose key is not NULL, push it onto `self.table[key]` (the right keys, the right schema);
- `next`: until the batch is full: hand out `pending` first; take the next left tuple (none: stop); compute its key (the left keys, the left schema) and look it up; for every right tuple found queue `left values ++ right values` (as a tuple with the plan's output schema); with no match, or a NULL key, queue `unmatched_output(..)` if it returns something.

## Tests

- The matching pairs come out; the result equals the nested loop join's.
- NULL keys match nothing, not even each other.
- Duplicates on both sides give every pair (2 left × 3 right = 6).
- Several key columns must all match, compared position by position.
- An empty side gives nothing; 2,000 × 1,000 rows join to 1,000.
- The join can be run twice.

## Syntax and methods

```rust
let table: HashMap<AggregateKey, Vec<Tuple>>;
self.table.entry(key).or_default().push(tuple);            // build: a Vec of tuples per key
self.table.get(&key)                                       // probe: Option<&Vec<Tuple>>
key.and_then(|k| self.table.get(&k))                       // Option<AggregateKey> -> Option<&Vec<Tuple>>
```

## Notes

**Which side builds.** The right side is built into the table and the left side probes, so the output keeps the left order of tuples. A real optimizer builds the *smaller* input; with BusTub's plan the right child is the build side, which a smarter rule (module 3h) could swap.

**The key expressions are per side.** The left key expressions are evaluated on left tuples with the left schema, and the right ones on right tuples with the right schema; both are plain `evaluate`, not `evaluate_join`, because each runs on one tuple. A join `a.x = b.y` has left key `[#0.x]` and right key `[#0.y]` (both `tuple_idx` 0 in their own side).

**NULL keys.** `NULL = NULL` is unknown, so a tuple with a NULL in its key neither goes into the table nor finds a match. That is the opposite of grouping (stage 1), where NULLs are one group; here the `AggregateKey` is reused but the NULL check happens before it.

**Memory.** The whole right side is in the table. If it does not fit, real systems partition both inputs by hash into pieces that do (*Grace hash join*) and join the pieces; BusTub does not.

## In BusTub

`hash_join_plan.h` (`LeftJoinKeyExpressions()`, `RightJoinKeyExpressions()`, the join type) and `p3.14-hash-join.slt`/`p3.15-multi-way-hash-join.slt` (`+ensure:hash_join` checks the plan). The executor `hash_join_executor.cpp` is the stub students fill.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unordered_map<AggregateKey, std::vector<Tuple>>` with a custom hash | `HashMap<AggregateKey, Vec<Tuple>>` (the key's `Hash`/`Eq` are stage 1) |
| `table_[key].push_back(tuple)` (default-inserts) | `table.entry(key).or_default().push(tuple)` |
| `auto it = table_.find(key); if (it != table_.end())` | `if let Some(matches) = table.get(&key)` |
| BusTub's hash simply skips NULL values (`if (!key.IsNull())`) | an explicit `Option` for "no key" |

**Port rule:** a multimap is a `HashMap<K, Vec<V>>`; "this row has no key" is an `Option<K>`.

## Learn more
- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html) · [`Option::and_then`](https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then) · SQLite [automatic indexes](https://www.sqlite.org/optoverview.html)

## Performance

Build is linear in the right side, probe linear in the left, and matching tuples are cloned into output: the cost is `|L| + |R| + |output|`. Memory is the build side. On a million rows each, a nested loop join takes about 10^12 predicate evaluations; this takes about 2 million hash operations.

**Measure it.** Join two tables of 2,000 and of 20,000 rows on equality with a hand-built plan and with a nested loop (`select ... join ... on a.x = b.y` runs the nested loop until module 3h); compare.

## Hints

### Evaluate keys with the right schema for the side

Using the left schema for a right tuple reads the wrong offsets and gives wrong keys, and equal-looking test data hides it until a VARCHAR column appears.

### A left tuple's matches can exceed a batch

As in the nested loop join: queue all matches in `pending`; return up to `batch_size` per call.

### Do not insert NULL-key tuples

If you put them in the table under some "null key", a left tuple with a NULL key will find them, which SQL forbids.
