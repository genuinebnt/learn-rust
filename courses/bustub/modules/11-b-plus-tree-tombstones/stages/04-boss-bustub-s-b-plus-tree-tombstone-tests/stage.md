BusTub's tombstone tests, ported, and the tombstone runs of its other B+ tree tests. Nothing new to write: if something fails, the test name says which stage's rule is wrong.

## The task

Make these pass:
- `b_plus_tree_tombstone_test`: `tombstone_basic_test`, `tombstone_split_test`, `tombstone_borrow_test`, `tombstone_coalesce_test` (BusTub's `b_plus_tree_tombstone_test.cpp`);
- `b_plus_tree_tombstone_variants_test`: the concurrent insert, delete and mix tests of module 2c run on a tree with `TOMBS = 3`, `SequentialEdgeMixTest` with `TOMBS = 2`, an optimistic insert and delete that still latch one leaf, and a random-operations test against a model for three buffer sizes.

## Tests

- All of the above: 4 + 9 tests.
- Run the concurrent ones many times: `for i in $(seq 20); do cargo test --test b_plus_tree_tombstone_variants_test || break; done`.

## Notes

**What BusTub does that this course does not pin.** BusTub's Project 2 specification (not part of its source tree) defines when a tombstone becomes a real removal. This course derived its rules from what the tests above require (stages 2 and 3) and states them on those pages; where BusTub's reference solution differs in a way no test observes, nothing here says it is wrong.

**Type parameters in the tests.** `new_tree_t::<2>(&bpm, 4, 4)` and `IndexLeaves::<2>::with_tombstones(..)` carry the buffer size; `check_structure_t::<T>` and `shape_t::<T>` are the matching test utilities.

## In BusTub

`test/storage/b_plus_tree_tombstone_test.cpp` (the four tests), and the `Tombs` template parameter of the insert, delete and concurrent tests ("InsertTest1Call<0>(); InsertTest1Call<3>();").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `BPlusTree<GenericKey<8>, RID, GenericComparator<8>, 2> tree(...)` | `BPlusTree::<Key, Rid, Cmp, 2>::new(...)` (a const generic argument) |
| `InsertTest1Call<3>()` (a function template called with a constant) | `fn insert_test_1_call<const T: usize>()` called as `insert_test_1_call::<3>()` |

## Learn more
- [BusTub's tombstone test](https://github.com/cmu-db/bustub/blob/master/test/storage/b_plus_tree_tombstone_test.cpp)

## Performance

The concurrent variants run the same workloads as stage 2c's boss with a leaf that does a little more per operation (the buffer scan). They should take about as long: if a tombstone variant is several times slower, look for a purge or a buffer rewrite that runs on the hot path (every insert, every search) instead of only on a short leaf or a full buffer.

**Measure it.** Time `mix_test_2_with_tombstones` in release mode and compare with `mix_test_2` of the 2c boss.

## Hints

### A failure only with tombstones

Run the same test with `TOMBS = 0` (module 2c's version) first: if that passes, the bug is in a tombstone rule. Then reduce the failing test's workload until `shape_t` of the tree before and after the failing operation fits on a screen, and read the rule that operation should have followed.

### The concurrency variants

If only the concurrent ones fail, check what the optimistic paths do with tombstones: a logical delete that needs no real removal must stay a one-leaf write, and a resurrecting insert must not insist on a free slot.

### Count latches, not time

`tree.bpm.get_writes()` before and after one operation tells you whether the fast path was taken. A delete that falls back to the slow path when it did not have to is a performance bug the tests catch with this counter.
