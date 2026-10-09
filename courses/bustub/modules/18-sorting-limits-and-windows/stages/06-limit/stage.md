`select * from t limit 10`: the **limit** executor passes on the first `n` tuples of its child and then stops. Its importance is what it does *not* do: once it has `n` tuples it never pulls from the child again, so `limit 5` over a scan of ten million rows touches a page, not a table. This is the pull model paying off.

## The task

In `src/execution/executors/limit_executor.rs` (the struct, `new` given; `self.limit` is the plan's limit, `self.emitted` the count so far):
- `init`: `emitted = 0` and initialise the child;
- `next`: if `emitted >= limit` return `false` without touching the child; otherwise ask the child for at most `batch_size.min(limit - emitted)` tuples; if it has none return `false`; truncate the batch (and the rids) to that many (a child may return more than it was asked for), add the batch length to `emitted`, and return `true` if the batch is not empty.

## Tests

- `limit 3`, `limit 1`, `limit 0`; a limit larger than the table returns the whole table.
- Limits that are not a multiple of the batch size (20, 21, 45, 99 of 100 rows).
- `select * from __mock_t9 limit 5` finishes at once: the mock table has **ten million** rows, so reading them all would not.
- `order by ... limit` and a limit inside a subquery.
- `init` starts the count over: two runs of the same executor each give 5 rows.

## Syntax and methods

```rust
let wanted = batch_size.min(self.limit - self.emitted);          // usize arithmetic: emitted < limit here
self.child.next(tuple_batch, rid_batch, wanted)?                 // pass the output vectors straight through
tuple_batch.truncate(wanted); rid_batch.truncate(wanted);
```

## Notes

**Do not read ahead.** Pulling a full batch from the child when only two more tuples are needed does work that is thrown away, and for an `insert ... select ... limit` or a join below, extra reads are not harmless. Ask for what you still need.

**Truncate anyway.** Asking for `wanted` tuples is a request, not a guarantee; an executor is allowed to return a slightly larger batch (batches are sized by what is convenient). Cut it down so the count is exact.

**Limit is not sort.** `limit 3` on its own returns any 3 rows (here: the first 3 in storage order). Together with `order by` the planner puts the limit above the sort; stage 7 shows how to avoid sorting everything for that pair.

**Zero.** `limit 0` returns nothing; because `emitted >= limit` on the very first call, the child is never even asked.

## In BusTub

`limit_executor.h`/`.cpp`, `limit_plan.h` (`LimitPlanNode(output, child, limit)`; the offset is not supported: the planner (given) rejects `OFFSET` with "OFFSET clause is not supported yet.").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min(batch_size, limit_ - emitted_)` | `batch_size.min(self.limit - self.emitted)` |
| `tuple_batch->resize(n)` | `tuple_batch.truncate(n)` |
| `child_executor_->Next(tuple_batch, rid_batch, wanted)` with the caller's out-vectors | the same: pass `&mut Vec`s through |
| `size_t` underflow if `emitted_ > limit_` | check `emitted >= limit` first; the subtraction cannot underflow |

**Port rule:** pass the caller's output vectors down to the child instead of copying through temporaries.

## Learn more
- [PostgreSQL: LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html) · [`Ord::min`](https://doc.rust-lang.org/std/cmp/trait.Ord.html#method.min) · [`Vec::truncate`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.truncate)

## Performance

`limit k` over a streaming child costs `O(k)`, independent of the table size. Over a blocking child (a sort, an aggregation) the child does all its work before the first tuple, so the limit saves only the output; that is why `sort + limit` is rewritten to a top-N.

**Measure it.** `limit 5` on `__mock_t9` and on a sort of 100,000 rows: the first is instant, the second sorts everything.

## Hints

### Check the count before the child

The `emitted >= limit` test comes first. If you ask the child before checking, `limit 0` still reads a batch.

### The batch you return may be shorter than asked

If the child has 3 tuples left and you asked for 10, you return 3 and `true`; the next call returns `false`. Do not loop until you have `wanted`.

### Count what you return

`emitted += tuple_batch.len()` after the truncate, not the number the child produced.
