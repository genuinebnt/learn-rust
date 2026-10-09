`update t set b = b + a where a >= 3`. Where an insert adds a row and a delete flags one, an update replaces a row by another whose columns are expressions of the old one. BusTub's plan is `Update ← Filter ← SeqScan` with one **target expression** per column of the table; the executor evaluates them on each old row and stores the result.

This course implements it as **delete + insert**: flag the old tuple deleted, store the new tuple (a new rid, since a longer string will not fit in the old slot), and move every index entry. It is the executor that exercises everything so far, and the one where the Halloween problem is a real risk: the update inserts into the very table its child is scanning.

## The task

In `src/execution/executors/update_executor.rs` (the struct, `new` given):
- `make_new_tuple(old)`: evaluate each of `self.target_expressions` on the old tuple, using the child's output schema, and build a tuple of those values with the **table's** schema;
- `init`: forget that the count was produced and initialise the child;
- `next`: once, for every `(old, old_rid)` the child produces: build the new tuple; flag the old heap tuple deleted and remove its entries from every index; insert the new tuple and add its key to every index under the **new rid**; count. Then answer with one tuple holding the count; later calls return `false`.

## Tests

- `update ... where` returns the count and changes exactly those rows; an update that matches nothing returns `0`.
- New values can use the old ones (`set b = b + a`), and all expressions see the *old* row (`set a = b, b = a` swaps).
- Every row is updated exactly once even though the new rows are stored at the end of the table (3,000 rows: `a = a + 1` gives `2..=3001`, not more).
- A string can become longer.
- The indexes follow: the old key is gone, the new key finds the new row; an unchanged key leads to the new tuple.

## Syntax and methods

```rust
let mut values = Vec::with_capacity(self.target_expressions.len());
for expr in &self.target_expressions { values.push(expr.evaluate(old, self.child.output_schema())?); }
Tuple::new(&values, &self.table_info.schema)
let new_rid = table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &new)?;
```

## Notes

**Targets are per column.** The planner (given) gives `target_expressions` one entry per column of the table: the user's expression for the columns in `SET`, and a plain column reference (`#0.i`) for the others. So the new tuple is just "evaluate every expression".

**All expressions see the old row.** `set a = b, b = a` evaluates both on the old tuple and builds the new one at once. Building the new tuple column by column from partly updated values would give `a = b, b = b`.

**Why the scan does not loop (Halloween).** The new rows land at the end of the table, after the point where the scan will stop: the scan was started with `make_iterator`, which records the end at that moment. If it used the eager iterator, the update would meet its own output and update it again, forever (module 3c, stage 3; the concept article *The Halloween problem*).

**Delete, then insert.** For an indexed column, remove the old key *before* you add the new one. If the update did not change the key, the order matters: insert-then-delete would remove the entry you just wrote. (Stage 4's note on duplicates: an update to a key that exists would be refused by the index.)

**Why not in place?** `TableHeap::update_tuple_in_place` exists, but only works when the new tuple has exactly the same length; a VARCHAR that grows would fail. Project 4 (MVCC) turns the in-place version into undo logs; here the simple, general version is the right one.

## In BusTub

`update_plan.h` (`UpdatePlanNode(SchemaRef output, AbstractPlanNodeRef child, table_oid_t table_oid, std::vector<AbstractExpressionRef> target_expressions)`), `plan_insert.cpp`'s `PlanUpdate` ("target_exprs.resize(filter->output_schema_->GetColumnCount()) ... fill the untouched columns with column references"), and `update_executor.cpp`'s contract: "Yield the number of rows updated in the table ... NOTE: UpdateExecutor::Next() returns true with the number of updated rows produced only once."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<Value> values; for (auto &expr : plan_->target_expressions_) values.push_back(expr->Evaluate(&old, child_schema));` | the same loop, with `?` on each `evaluate` |
| `table_heap->InsertTuple(meta, new_tuple)` returning `optional<RID>` | `insert_tuple(&meta, &new)?` |
| remembering rids to avoid the Halloween problem by hand | the iterator's stopping rid does it |

**Port rule:** a statement that reads and writes the same table is safe only if the reader cannot see the writer's output: snapshot the end (or the whole input) first.

## Learn more
- [Halloween problem](https://en.wikipedia.org/wiki/Halloween_Problem) · PostgreSQL [heap-only tuples](https://www.postgresql.org/docs/current/storage-hot.html) · [`Vec::with_capacity`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity)

## Performance

An update costs a delete and an insert plus an index delete and insert per index: four writes for a one-index table even if the change was tiny. In-place updates and PostgreSQL's HOT updates exist to avoid exactly this. Also notice the table grows by the number of updated rows until something reclaims the flagged slots.

**Measure it.** Update every row of a 100,000-row table and time a `select *` before and after: the scan walks twice as many slots.

## Hints

### Evaluate before you change anything

Compute the new tuple first (`make_new_tuple`), then touch the heap. A failing expression (overflow) must not leave a half-updated row.

### The new rid, not the old one

The index entry for the new tuple must carry `new_rid`. The test `updating_a_column_that_is_not_in_the_key` looks up the unchanged key and expects the *new* value.

### Which schema evaluates, which lays out

Target expressions are evaluated against the *child's* tuples (the scan's output schema) but the new tuple is laid out with the *table's* schema. They have the same shape here, and mixing them is a bug waiting for a VARCHAR column to expose it.
