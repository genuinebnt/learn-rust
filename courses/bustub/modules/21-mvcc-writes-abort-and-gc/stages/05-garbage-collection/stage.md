Every update leaves a log; every transaction stays in the transaction manager's map as long as its logs might be read. Nothing ever shrinks unless somebody works out what is no longer needed. This stage writes that somebody. In BusTub it is **stop-the-world**: you may assume no transaction is executing a statement while it runs.

## The task

In `src/concurrency/transaction_manager.rs`, `garbage_collection(&self)`, the region marked `4b-05`:

1. `watermark = self.get_watermark()`.
2. For every table in the catalog (`catalog.get_table_names()`, `get_table(name)`), for every tuple (`make_eager_iterator`): read its metadata and head link (`get_tuple_and_undo_link`).
   - If the tuple's timestamp is at or below the watermark, no reader can need anything below it: clear its link (`update_undo_link(rid, None, None)`) and go on.
   - Otherwise walk its chain from the head: for each log note the **transaction that owns it** as *needed*; stop after the first log whose `ts` is at or below the watermark (it is the oldest version anybody can ask for). A log that can't be fetched ends the walk.
3. Keep in `txn_map` exactly the transactions that are `Running` or `Tainted`, or *needed*; drop the rest.

## Tests

- A finished transaction with no logs is forgotten; a running one stays.
- A transaction whose logs an older reader may need stays; once that reader ends it goes, and the data still reads right.
- Only logs below the oldest needed version go: a chain keeps what a mid-aged reader needs.
- Tainted and running transactions are never collected; an aborted one is, once nothing links to it.
- Collecting twice changes nothing, and every snapshot still reads the same.

## Syntax and methods

```rust
let watermark = self.get_watermark();
let mut needed: HashSet<TxnId> = HashSet::new();
let catalog = self.catalog.read().unwrap();
for name in catalog.get_table_names() {
    let Some(table) = catalog.get_table(&name) else { continue };
    let mut iter = table.table.make_eager_iterator();
    while !iter.is_end() { let rid = iter.get_rid(); iter.advance(); ... }
}
self.txn_map.write().unwrap().retain(|id, t| matches!(t.state(), Running | Tainted) || needed.contains(id));
```

## Notes

**Needed means reachable at or above the watermark.** The chain from a tuple whose timestamp is above the watermark leads, newest first, through versions some running reader may want. The reader with the smallest read timestamp (the watermark) wants the first version with `ts <= watermark`; everything older is garbage. All of the logs *up to and including* that one are needed; the transactions that own them cannot be forgotten.

**One transaction, many chains.** A transaction owns logs in many chains. It is needed if *any* of them is. That is why you collect a set across all tuples first and delete afterwards.

**Running and tainted stay for their own reasons.** They may yet write, or abort and need their logs; and their *read* state matters to the watermark.

**What is not freed.** Tombstones stay in the table. Real systems also reclaim table space and index entries after garbage collection (PostgreSQL's `VACUUM`); this exercise only forgets transactions and chain links.

## In BusTub

`transaction_manager.cpp`: "`/** @brief Stop-the-world garbage collection. Will be called only when all transactions are not accessing the table heap. */ void TransactionManager::GarbageCollection() { UNIMPLEMENTED("not implemented"); }`". `TxnExecutorTest.GarbageCollection` ("A: first GC", "B: second GC (yes, we call it twice without doing anything)", "C" to "F") and `GarbageCollectionWithTainted` run it with `EnsureTxnGCed` / `EnsureTxnExists`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unordered_set<txn_id_t>` and erasing from `txn_map_` in a loop | `HashSet<TxnId>` and `HashMap::retain` |
| a shared lock on the catalog while iterating tables | `self.catalog.read().unwrap()` held for the whole walk |

**Port rule:** "erase while iterating" in C++ is `retain` in Rust: one pass with a predicate, no iterator invalidation.

## Learn more
- [`HashMap::retain`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.retain) · [PostgreSQL: routine vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html) · [Garbage collection in Wu et al.](https://www.vldb.org/pvldb/vol10/p781-Wu.pdf)

## Performance

One pass over every tuple of every table, plus chain walks that stop at the watermark: linear in the size of the database (plus the length of the chains still in use). That is why real systems collect per page in the background; the stop-the-world version is a stand-in for the algorithm, not a way to run a server.

**Measure it.** Build a table of 100 000 rows with one committed update each, then time `garbage_collection()` with and without a long-running old reader.

## Hints

### The first log at or below the watermark is included

Stop *after* adding its transaction to the set, not before. The reader at the watermark needs it.

### Collect first, delete second

A transaction is needed if any chain still reaches it. Deleting while walking would forget transactions whose logs are reached by a chain visited later.

### A tuple at or below the watermark ends its chain

Its timestamp is already visible to every possible reader, so even its head link is dead weight. Clear it so that no link dangles to a forgotten transaction.
