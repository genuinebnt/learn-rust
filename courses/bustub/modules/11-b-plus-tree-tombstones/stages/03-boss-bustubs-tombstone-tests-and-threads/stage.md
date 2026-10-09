**Where this fits.** The end of the index modules: BusTub's four tombstone scenarios and the tombstone runs of its concurrent tests, plus a threaded workload and a long random run for every buffer size.

> [!CHECK] Six threads work on a tree with a tombstone buffer of 3: two insert a range of keys, two delete the same keys, two keep looking up keys nobody touches. What must be true at the end for the untouched keys, and what is *not* determined about the keys the writers fought over?
> ||The untouched ("preserved") keys must all be found by lookups throughout and by a scan at the end: nothing a writer does may lose, hide or duplicate them. For the contested keys each may be present or absent at the end (it depends on which of the inserting and deleting threads ran last on that key); what is determined is only that the structure is valid: every leaf rule holds and a scan equals exactly the set of keys that are live.||
>
> - Which keys does the test assert on?
> - Which structural rules are checked at the end?
> - What would a lost update look like?

## The task

Nothing new to design.

- **Threads.** Six threads on a `TOMBS = 3` tree: two insert 360 contested keys, two delete them, two read 40 preserved keys; five rounds. At the end every preserved key is in the scan, `check_shape_t` holds for whatever set of keys is live, no page stays pinned, and the whole thing finishes under a timeout.
- **Long runs.** 1 500 random operations for leaf sizes and fan-outs `(2,3) (3,3) (4,4) (5,4) (6,7)`, buffer sizes 1, 2 and 3, three seeds each: the live keys equal a `BTreeSet` and `check_shape_t` holds every 25 steps.
- **BusTub's tests.** `b_plus_tree_tombstone_test.rs` (`tombstone_basic_test`, `tombstone_split_test`, `tombstone_borrow_test`, `tombstone_coalesce_test`) and `b_plus_tree_tombstone_variants_test.rs` (the concurrent insert, delete and mix tests, the sequential edge mix, the optimistic latch count, and a random workload for every buffer size), all with `TOMBS > 0`.

## Your freedom

The same as before.

## The Rust toolbox

**Generic tests over a const.** The variants file calls `insert_test_1_call::<3>()`: one function per scenario, instantiated for each buffer size.

**Running the slow ones.** The variants file repeats each concurrent scenario 50 times; run one with `cargo test --release --test b_plus_tree_tombstone_variants_test mix_test_1`.

## If this is new

- Everything is in the earlier stages of this module and of 2c.

## Tests

- Threads deleting, inserting and reading keep every preserved key and a valid structure.
- Long random runs for every buffer size agree with a set.
- BusTub's four tombstone scenarios and the tombstone variants of its concurrent tests.

## Hints

### A scenario test fails

Each BusTub scenario has the leaf renderings written out in stage 2d-02's tests; reproduce it by hand with `leaves_t(&tree)` printed after every call and compare with your reading of the rules.

### A concurrent variant fails

Check whether it also fails with `TOMBS = 0`; if not, a tombstone path takes a latch the plain path does not, or releases one early.

## Performance

The variants file takes tens of seconds in debug mode because each concurrent scenario runs 50 times. Release mode brings it down to seconds.

## Experiment

Optional. Predict first, then run.

1. **Bigger buffers under threads.** Run the thread test with `TOMBS = 16`. Does contention go up or down, and why?
2. **Tombstone-heavy workload.** Delete 95% of a tree's keys and compare scan speed with `TOMBS = 0` and `TOMBS = 3`.

## Other designs

None for this stage. The *Other designs* sections of 2d-01 and 2d-02 list the alternatives to compare with yours.

## In BusTub

The tombstone tests are the optional extension of Project 2 in recent years; passing them is the evidence that your index handles logical deletes through every structural operation.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TEST(BPlusTreeTombstoneTest, TombstoneBasicTest)` | `#[test] fn tombstone_basic_test()` |
| `LaunchParallelTest(2, ...)` | `thread::scope` with two spawns |
| `GetTombstones()` on a leaf page | `tree.leaf_tombstones()` |

**Port rule:** an accessor on a page class becomes an observer on the tree.

## Learn more

- [`thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html) · BusTub's tombstone tests in [`b_plus_tree_tombstone_test.cpp`](https://github.com/cmu-db/bustub/tree/master/test/storage)
