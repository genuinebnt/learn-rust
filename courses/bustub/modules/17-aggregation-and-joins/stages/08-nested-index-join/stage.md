If the right table has an index on the join column, a join does not need to scan it at all: for each left tuple, **ask the index** for the matching rows. That is the **nested index join**, the third join algorithm. With a small left side and a huge indexed right side it beats a hash join (no table of millions to build), because each probe costs a few page reads.

BusTub's optimizer (given, in the "starter" rules) rewrites an equality nested loop join whose right side is a scan of an indexed column into a `NestedIndexJoin` plan. Turn it on with `set force_optimizer_starter_rule=yes`; `explain` then shows `NestedIndexJoin { type=Inner, key_predicate=#0.0, index=..., index_table=... }`. This stage writes the executor.

## The task

In `src/execution/executors/nested_index_join_executor.rs` (the struct, `new` (it looks up the inner table and the index in the catalog), and the `TupleStream` over the outer child are given):
- `probe(outer) -> Result<Vec<Tuple>>`: evaluate `self.key_predicate` on the outer tuple (with the child's schema) to get the key value (a NULL key matches nothing); make a one-column key tuple with the index's key schema; look it up (`self.index.index.scan_key(&key)`); fetch each rid from the inner table (`self.inner_table.table.get_tuple(rid)?`) and keep the tuples that are **not deleted**;
- `init`: forget pending output and initialise the child;
- `next`: until the batch is full: hand out `pending` first; take the next outer tuple (none: stop); `probe` it; for every inner tuple queue `outer values ++ inner values` (laid out with the plan's output schema); if there is none and the join is a **LEFT** join, queue the outer values followed by NULLs for the inner columns (`nulls_for(&self.inner_schema)`).

## Tests

- The optimizer turns the equality join on an indexed column into an index join (`explain`).
- Inner join through the index (the equality may be written either way round); left join pads unmatched outer rows.
- A deleted inner row is not joined; rows inserted after the index was made are found.
- The result equals the nested loop join's on a bigger table (300 outer rows against 100 indexed inner rows).
- Without an index the join stays a nested loop.

## Syntax and methods

```rust
let key = Tuple::new(&[key_value], &self.index.key_schema);        // the index's key layout
for rid in self.index.index.scan_key(&key) {                       // Vec<Rid>: 0 or 1 here
    let (meta, tuple) = self.inner_table.table.get_tuple(rid)?;
    if !meta.is_deleted { found.push(tuple); }
}
values_of(&inner, &self.inner_schema)                              // inner_schema: the schema of the inner scan's tuples
```

## Notes

**The plan hands you the pieces.** `NestedIndexJoinPlanNode` carries the `key_predicate` (an expression over the *outer* tuple: "the value to look up"), the inner table's oid and schema, and the index oid. The executor does not search the catalog for an index by columns; the optimizer already chose it.

**Borrowing from the catalog.** `new` (given) keeps `&'e TableInfo` for the inner table and an `Arc<IndexInfo>`, both valid for the whole query; `probe` uses them without lookups. The index is not the truth: the fetched row is checked for `is_deleted`.

**One inner row per key here.** The B+ tree keeps unique keys, so `scan_key` returns at most one rid and a key joins at most one inner row; for a non-unique index (a duplicate was refused at insert, module 3e) the index join would miss the duplicates. The nested loop and hash joins have no such limit, which is why the optimizer should only use an index join on a unique column.

**Left join.** If `probe` finds nothing the outer tuple is output once with typed NULLs for the inner columns (`inner_schema` is the schema of the inner scan; it has the same columns as the table).

## In BusTub

`nested_index_join_plan.h` (`NestedIndexJoinPlanNode(output, child, key_predicate, inner_table_oid, index_oid, index_name, index_table_name, inner_table_schema, join_type)`), `nlj_as_index_join.cpp` (the rule: "optimize nested loop join into index join"; `MatchIndex(table_name, index_key_idx)`), and `p3.13-nested-index-join.slt`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `index->ScanKey(Tuple({key_value}, index->GetKeySchema()), &rids, txn)` | `index.scan_key(&Tuple::new(&[key_value], &index.key_schema))` |
| `table_info->table_->GetTuple(rid)` then check `meta.is_deleted_` | the same, with `?` |
| dynamic_cast to `BPlusTreeIndexForTwoIntegerColumn *` to reach the tree | the `Index` trait; no cast |
| `std::unique_ptr` to the table and index infos from the catalog on each call | references kept from construction |

**Port rule:** an executor that needs a catalog object looks it up once, in the constructor, and keeps a borrow.

## Learn more
- [Use The Index, Luke: nested loops](https://use-the-index-luke.com/sql/join/nested-loops-join-n1-problem) · PostgreSQL [Nested Loop with an Index Scan](https://www.postgresql.org/docs/current/using-explain.html) · [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html)

## Performance

`|L| × (tree height + 1)` page reads: for 1,000 outer rows and a million-row indexed inner table, about 4,000 page reads against reading the whole inner table (tens of thousands of pages) for a hash join. But for a *large* outer side the random page accesses lose to one sequential build: the optimizer has to choose.

**Measure it.** Join outer sizes 10, 1,000 and 100,000 against a 100,000-row indexed table with the index join (`set force_optimizer_starter_rule=yes`) and with the hand-built hash join of stage 6.

## Hints

### Key from the outer tuple, layout from the index

`key_predicate.evaluate(outer, child_schema)` gives the value; `Tuple::new(&[value], &index.key_schema)` is the key the index understands. Using the inner *table's* schema for the key puts bytes at the wrong offsets for any column but the first.

### NULL outer keys

`NULL = anything` is not true: skip the probe, and in a left join output the outer tuple padded. A NULL key tuple sent to the index would compare as the integer `i32::MIN`.

### Check the table, not just the index

An index entry can name a deleted row; skip it (`is_deleted`) so the left join pads, rather than joining a ghost.
