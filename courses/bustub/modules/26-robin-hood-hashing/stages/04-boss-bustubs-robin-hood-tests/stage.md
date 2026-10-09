BusTub's concurrent Robin Hood tests, ported: sixteen threads insert the same key; writers and readers overlap; eight threads race to remove the same keys; eight threads run overlapping inserts, lookups and removes; and a big table takes 200 000 inserts.

## The task

Make the stage's tests pass: `cargo test --test stages_0c s0c_04`.

The tests: BusTub's concurrent ones (sixteen threads inserting the same key; writers and readers that do not lose keys; each key removed exactly once whoever races; overlapping inserts, lookups and removes that finish and keep the size sane; a big table taking two hundred thousand inserts) and the stage 2 and 3 properties.

## Your freedom

None new.

## The Rust toolbox

**Barriers in tests.** `std::sync::Barrier` makes the threads start together so that races actually happen.

**Reading a failure.** The race tests print the key and the thread; check `size()` against `contains` for every key afterwards: the first disagreement tells you which lock is missing.

## Design notes

**What the stress test catches.** `size` is updated inside the same critical section as the buckets, so after the threads finish, `size()` must equal the number of keys `contains` finds. A mismatch means a counter was changed outside the lock, or a key was lost in a displacement.

**Not ported.** BusTub's `ParallelSpeedupTest` requires lock striping so that independent inserts run in parallel; a single reader-writer lock serialises writers, so the port leaves it out. Striping is the natural extension: a displacement chain can cross stripes, so stripes must be locked in a fixed order.

## If this is new

- Everything is in the earlier stages of this module.

## Tests

- BusTub's five concurrent tests; the properties of the earlier stages.

## Hints

### Keep every update of `size` under the lock

The same guard that changes a bucket changes the count.

### If a key goes missing

Run the model-check test of stage 3 first; a displacement bug shows there deterministically.

## Performance

Two hundred thousand inserts take a fraction of a second in release mode and a few seconds in debug.

## Experiment

Optional. Predict first, then run.

1. **Use a `Mutex` instead of `RwLock`.** Does any test fail? What does it cost in the readers test?
2. **Fewer buckets than keys.** What does the 200 000-insert test do with a capacity of 100 000?

## Other designs

None for this stage. The *Other designs* sections of 0c-01 to 0c-03 list the alternatives to compare with yours.

## In BusTub

`test/primer/robin_hood_hash_set_test.cpp`: `ConcurrentDuplicateInsertTest`, `ConcurrentInsertAndLookupTest`, `ConcurrentRemoveTest`, `ConcurrentOverlappingOperationsStressTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `ThreadGate` built from a mutex and two condition variables | `std::sync::Barrier` |

**Port rule:** "all threads start together" is a `Barrier`.

## Learn more

- [`Barrier`](https://doc.rust-lang.org/std/sync/struct.Barrier.html)
