BusTub's concurrent Robin Hood tests, ported: sixteen threads insert the same key; writers and readers overlap; eight threads race to remove the same keys; eight threads run overlapping inserts, lookups and removes; and a big table takes 200 000 inserts.

## The task

Make the stage's tests pass: `cargo test --test stages_0c s0c_04`.

## Tests

- `s0c_04_sixteen_threads_insert_the_same_key`: all succeed, one key.
- `s0c_04_writers_and_readers_do_not_lose_keys`.
- `s0c_04_each_key_is_removed_exactly_once_whoever_races`.
- `s0c_04_overlapping_inserts_lookups_and_removes_finish_and_keep_the_size_sane`: the final size equals the number of keys a lookup finds.
- `s0c_04_a_big_table_takes_two_hundred_thousand_inserts`.

## Notes

**What the stress test catches.** `size` is updated inside the same critical section as the buckets, so after the threads finish, `size()` must equal the number of keys `contains` finds. A mismatch means a counter was changed outside the lock, or a key was lost in a displacement.

**Not ported.** BusTub's `ParallelSpeedupTest` requires lock striping so that independent inserts run in parallel; a single reader-writer lock serialises writers, so the port leaves it out. Striping is the natural extension: a displacement chain can cross stripes, so stripes must be locked in a fixed order.

## In BusTub

`test/primer/robin_hood_hash_set_test.cpp`: `ConcurrentDuplicateInsertTest`, `ConcurrentInsertAndLookupTest`, `ConcurrentRemoveTest`, `ConcurrentOverlappingOperationsStressTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `ThreadGate` built from a mutex and two condition variables | `std::sync::Barrier` |

**Port rule:** "all threads start together" is a `Barrier`.

## Learn more
- [`Barrier`](https://doc.rust-lang.org/std/sync/struct.Barrier.html)

## Performance

One lock serialises writes: throughput does not improve with threads, but correctness does not depend on them. Reads share.

**Measure it.** Compare 1 and 8 reader threads over a read-only table: throughput should scale with cores.

## Hints

### Keep every update of `size` under the lock

The same guard that changes a bucket changes the count.

### If a key goes missing

Run the model-check test of stage 3 first; a displacement bug shows there deterministically.
