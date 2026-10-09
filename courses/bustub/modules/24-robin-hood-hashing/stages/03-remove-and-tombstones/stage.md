Emptying a bucket on removal would cut the probe chains of keys that went past it. Instead `remove` leaves a **tombstone**: lookups probe past it, inserts may reuse it. This stage adds `remove`, `clear` and the statistic `max_probe_distance`, and checks the whole set against Rust's `HashSet` on a random workload.

## The task

In `src/primer/robin_hood_hash_set.rs`:

- `remove(&key) -> bool`: write lock; `find`; absent: `false`; else put a `Tombstone` in the bucket, size - 1, `true`.
- `clear()`: write lock; every slot `Empty`; size 0.
- `max_probe_distance()`: read lock; the largest `probe_distance(home, bucket)` over **live** buckets; 0 for an empty table. Tombstones do not count.

## Tests

- Remove reports whether the key was there; a lookup continues past a tombstone.
- Insert reuses a tombstone and the table stays consistent.
- `max_probe_distance` ignores tombstones (BusTub's scenario).
- A key stays reachable when a tombstone in front of it is reused.
- A random workload of inserts and removes agrees with a `HashSet` after every step.
- A table full of tombstones accepts inserts again; `clear` keeps the capacity.

## Syntax and methods

```rust
let Some(bucket) = self.find(&table, key) else { return false };
table.slots[bucket] = Slot::Tombstone;
table.size -= 1;
(0..self.capacity).filter_map(|b| match &table.slots[b] { Slot::Live(k) => Some(self.probe_distance(self.home_bucket(k), b)), _ => None }).max().unwrap_or(0)
```

## Notes

**The size counts live keys only.** Tombstones are neither in `size` nor free of cost: they lengthen probes. A workload that inserts and removes many different keys fills the table with tombstones; BusTub's header says nothing about rebuilding, so this exercise does not either (the full-table check uses `size`, and inserts reuse tombstones, so the table never blocks while a free bucket exists).

**The model check.** A random workload mixing inserts and removes, checked against `HashSet` after *every* operation (size and membership), is a cheap way to find the bug that hand-written cases miss. The early-exit bug of stage 2 is found by it within a few hundred operations.

**Clear while others read.** `clear` takes the write lock; a concurrent `contains` sees either the old or the empty table, never a half-cleared one.

## In BusTub

`robin_hood_hash_set.cpp`: "`@TODO(student) Mark an occupied matching slot as a tombstone without breaking concurrent operations.`". Tests: `TombstoneDeletionTest`, `TombstoneReuseTest`, `MaxProbeDistanceTest`, `ClearTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `state_` byte set to `kTombstone` | `Slot::Tombstone` |
| `std::unordered_set` as the model in a randomised test | `std::collections::HashSet` |

**Port rule:** a model-based test drives the structure and a trusted one with the same operations and compares after each.

## Learn more
- [Model-based testing](https://en.wikipedia.org/wiki/Model-based_testing) · [Tombstones in hash tables](https://en.wikipedia.org/wiki/Open_addressing#Disadvantages)

## Performance

Remove is a `find` plus one store. Tombstones cost probe length: after heavy churn a table needs a rebuild (not required here). `max_probe_distance` is a full scan, `O(capacity)`; it is a diagnostic, not a hot path.

**Measure it.** Insert and remove 1 000 000 different keys through a table of 1 024 buckets; watch lookups of absent keys slow as tombstones accumulate.

## Hints

### Remove only what `find` found

Do not mark a bucket as a tombstone unless `find` returned it as holding the key.

### Compare against the model every step

Assert `size()` and a handful of `contains` after each operation; the first failing step is the bug.

### Tombstones are not live

`max_probe_distance` and `size` must skip them; `insert`'s duplicate check must not match them.
