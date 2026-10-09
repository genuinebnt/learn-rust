`insert into t values (1, 'x'), (2, 'y')` and `insert into t select * from other` run as the same plan: an **Insert** node over a child that produces the rows (`Values` or a scan). The insert executor drains its child, stores every tuple in the table heap, and answers with **one row containing how many it inserted**. It is the first *pipeline breaker* you write: its first `next` does all the work, and every later call says "nothing more".

## The task

In `src/execution/executors/insert_executor.rs` (the struct, `new`, the `insert_into_indexes` helper (a stub until stage 4) are given):
- `init`: forget that the count was produced (`done = false`) and initialise the child;
- `next`: if `done`, return `false`. Otherwise pull batches from the child until it is exhausted; store each tuple with `table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, tuple)?`, call `insert_into_indexes(tuple, rid)` with the rid you got back, and count them. Then set `done`, put **one** tuple holding the count (an INTEGER, with the plan's output schema) in the batch (and a default rid), and return `true`.

## Tests

- `insert into t values (...)` returns the number of rows, and `select` then shows them in order.
- `insert into dst select ... where ...` copies a query's rows (a table can even insert from itself without looping); inserting nothing still answers `0`.
- The count is produced once: the second `next` returns `false` and nothing is inserted twice.
- 2,500 rows (more than a page and more than a batch) go in.
- Wrong inserts (a string for an INTEGER, the wrong number of columns, an unknown table) are errors before any row is stored.

## Syntax and methods

```rust
self.table_info.table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &tuple)?   // Result<Rid>
let (mut tuples, mut rids) = (vec![], vec![]);
while self.child.next(&mut tuples, &mut rids, BUSTUB_BATCH_SIZE)? { for t in &tuples { .. } }
tuple_batch.push(Tuple::new(&[Value::integer(count)], &self.plan.output_schema));
```

## Notes

**One answer.** `INSERT` returns a one-row, one-column result: the count. BusTub's header says so twice: "NOTE: InsertExecutor::Next() does not use the `rid_batch` out-parameter" and "returns true with the number of inserted rows produced only once". The `done` flag is that "once".

**Drain, then answer.** An insert could answer after each batch, but the contract is one row at the end. Draining also means the child (a scan of the *same table*) has finished before you report, and it has not seen your inserts (the scan stops where the table ended when it began).

**Tuples are stored as given.** The planner (given) already checked that the child's column types match the table's; the child's tuples have the table's byte layout, so no conversion is needed. A tuple too large for a page is an `Err` from `insert_tuple`, which `?` passes up and which aborts the statement.

**Count in an `i32`.** `Value::integer(count)` wants an `i32`; the count of a statement fits.

## In BusTub

`insert_executor.cpp`: "Yield the number of rows inserted into the table. @param[out] tuple_batch The tuple batch with one integer indicating the number of rows inserted into the table @param[out] rid_batch The next tuple RID batch produced by the insert (ignore, not used) ... NOTE: InsertExecutor::Next() returns true with the number of inserted rows produced only once."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<RID> rid = table_heap->InsertTuple(meta, tuple); if (!rid) { ... }` | `insert_tuple(..)?` returns `Result<Rid>` |
| a `bool has_inserted_` member | a `done: bool` field reset by `init` |
| `std::vector<Value> values{ValueFactory::GetIntegerValue(count)}; Tuple(values, &GetOutputSchema())` | `Tuple::new(&[Value::integer(count)], &self.plan.output_schema)` |
| `while (child_executor_->Next(&batch, &rids, batch_size))` | `while self.child.next(&mut batch, &mut rids, size)?` |

**Port rule:** a "have I already answered" member becomes a field `init` resets; `std::optional<RID>` failure becomes `Result`.

## Learn more
- [`?` and `Result`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) · [BusTub's insert executor](https://github.com/cmu-db/bustub/blob/master/src/execution/insert_executor.cpp) · PostgreSQL [INSERT](https://www.postgresql.org/docs/current/sql-insert.html)

## Performance

Each tuple insert latches the heap's last page and writes a slot: the cost is a lock acquisition, a page write and, once per page, a new page. Inserting 1,000,000 rows one statement at a time also pays parse and plan costs a million times, which is why bulk loads use one big `INSERT` or a dedicated loader.

**Measure it.** Insert 100,000 rows as one statement and as 100,000 one-row statements; the gap is the per-statement overhead (parse, bind, plan, optimise, build executors).

## Hints

### Insert one row at a time? No: one batch at a time

Loop over the batch you got; the child produces up to 20 tuples per call. The outer loop over `next` ends when it returns `false`.

### The count is not the number of batches

Count tuples, not calls to `next`.

### `init` must reset `done`

A parent may call `init` again; if `done` stays true the second run answers nothing. (Only `init` on the child is not enough.)
