`select * from emp join dept on emp.dept_id = dept.id`: for every row of the left input, find the rows of the right input for which the join predicate is true, and output each pair. The **nested loop join** does it the obvious way, two loops: for each left tuple, scan the whole right side. It is the only join that accepts *any* predicate (`a.x < b.y`, `a.x + 1 = b.y`), so every engine has one, and it is the baseline the other joins are checked against.

The executor is also the first with **two children** and with output that can be larger than its input: one left tuple can match many right tuples, more than fit in one batch. The state machine you write here (current left tuple, restart the right side, queue pending output) is the pattern of every join.

## The task

In `src/execution/executors/nested_loop_join_executor.rs` (the struct, `new`, the `TupleStream` wrappers around the children, `values_of`, `joined` and the LEFT-join helper `unmatched_output` are given; `unmatched_output` returns nothing until stage 5):
- `init`: initialise both children (`self.left.init()?`, `self.right.init()?`) and forget the current left tuple, the `matched` flag and any pending output;
- `next`: until the batch is full: first hand out `pending` output; if there is no current left tuple, take the next one from `self.left` (none: stop) and **initialise the right side again**; take the next right tuple and, if the predicate `evaluate_join` is TRUE for the pair, queue the joined tuple (`self.joined(left, &right)`) and set `matched`; when the right side is exhausted, queue `unmatched_output(..)` if it returns something and drop the left tuple. Return `true` if the batch is not empty.

## Tests

- An inner join outputs the matching pairs; the predicate can have other conditions (`and b.z > 200`) and need not be equality (`<`, `a.x + 1 = b.y`).
- NULL never matches (`NULL = NULL` is unknown).
- A cross join (`from a, b`) has every pair; with `where` the optimizer merges the filter into the join.
- One left row with 70 matches (more than a batch) outputs all of them.
- An empty side gives no rows; three tables and a table joined with itself work.
- The right side is re-initialised for each left tuple (`+ensure:nlj_init_check`).

## Syntax and methods

```rust
self.left.next()? -> Option<(Tuple, Rid)>                   // TupleStream: one tuple at a time, None at the end
self.right.init()?                                          // restart the inner side
self.predicate.evaluate_join(left, self.left.output_schema(), &right, self.right.output_schema())?   // Value
answer.as_bool() == Some(true)
self.pending.push_back(t); self.pending.pop_front()          // VecDeque: output waiting to be handed out
```

## Notes

**Two loops, unrolled.** The textbook is `for l in left { for r in right { .. } }`. An executor cannot keep loops on the stack between calls to `next`, so the loop variables become fields: `current_left` (the outer loop's variable), the right child's own cursor (the inner loop's), and `pending` for outputs produced but not yet returned. Each call to `next` resumes where the last stopped.

**Restart the inner side per outer tuple.** That is `self.right.init()?` whenever you take a new left tuple. The check `+ensure:nlj_init_check` wraps both children and verifies the right side is initialised about as often as the left produces tuples. Cache the right side in memory instead and you avoid re-reading, but the test notices (and a big right side would not fit).

**Output can exceed the batch.** One call fills at most `batch_size`, but a left tuple's matches can be more: queue them in `pending` and hand them out over several calls. If you push straight into `tuple_batch` and stop at the size limit you will lose or reorder matches.

**Unsupported join types.** `new` (given) refuses RIGHT and FULL joins with a `NotImplemented` error; only INNER and LEFT are built.

## In BusTub

`nested_loop_join_executor.cpp` (the stub: `UNIMPLEMENTED("TODO(P3): Add implementation.")`), `nested_loop_join_plan.h` (`predicate_`, `join_type_`, left and right plans) and `p3.10-simple-join.slt`, whose first real test is `query rowsort +ensure:nlj_init_check select * from test_simple_seq_1 s1 inner join test_simple_seq_2 s2 on s1.col1 + 5 = s2.col1;`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `left_executor_->Next(&left_batch, &left_rids, batch_size)` and index juggling over two batches | `TupleStream::next()` hides the batches and gives one tuple |
| `plan_->Predicate().EvaluateJoin(&l, left_schema, &r, right_schema)` | `predicate.evaluate_join(&l, ls, &r, rs)?` |
| `std::deque<Tuple>` for pending output | `VecDeque<Tuple>` |
| `for (...) { for (...) { ... } }` | a state machine over fields, resumed by each `next` |

**Port rule:** nested loops that must pause become state in the struct; one `if` per loop level decides which level to advance.

## Learn more
- [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · [PostgreSQL: table expressions and joins](https://www.postgresql.org/docs/current/queries-table-expressions.html) · [How the PostgreSQL planner picks a join](https://www.postgresql.org/docs/current/planner-optimizer.html)

## Performance

`|L| × |R|` predicate evaluations, and `|L|` restarts of the right child: for two tables of 10,000 rows that is 100 million evaluations; for a million each, a trillion. The inner scan hits the buffer pool each time (cheap if the right side fits in memory, ruinous if not). This is the reason hash joins exist.

**Measure it.** Join two tables of 1,000 and then 2,000 rows on an equality and watch the time quadruple.

## Hints

### Restart the right side exactly when you take a new left tuple

Not before the first left tuple (a fresh `init` already did it) and not after the last one. The check tolerates one off, not many.

### The matched flag is per left tuple

Reset it when you take a new left tuple; set it when any pair matches. Stage 5 reads it when the right side runs out.

### `pending` first

At the top of each loop turn, return queued output before doing any more work; otherwise you can leave the loop with output still queued and `next` returns `false` while rows are waiting.
