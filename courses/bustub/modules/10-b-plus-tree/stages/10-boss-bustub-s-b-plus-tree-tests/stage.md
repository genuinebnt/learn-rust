This is the finish line: BusTub's own B+ tree tests, ported test for test. They are the checks the original project's autograder runs on a student's tree (insert, delete, a 5,000-key scale test, and the concurrent tests), and your tree must pass them unchanged. There is nothing new to implement; if one fails, the failing test names the stage whose behaviour is wrong.

## The task

Make these test files pass (`cargo test --test <name>`, or `anneal course test`):
- `b_plus_tree_insert_test`: `basic_insert_test`, `optimistic_insert_test` (counts the write latches of an insert into a leaf with room), `insert_test_1_no_iterator`, `insert_test_2` (with iterators);
- `b_plus_tree_delete_test`: `delete_test_no_iterator`, `optimistic_delete_test`, `sequential_edge_mix_test`;
- `b_plus_tree_sequential_scale_test`: `basic_scale_test` (5,000 shuffled keys, leaf size 2, internal size 3, a pool of 30 frames);
- `b_plus_tree_concurrent_test`: `insert_test_1`, `insert_test_2`, `delete_test_1`, `delete_test_2`, `mix_test_1` and `mix_test_2` (two to ten threads each, repeated 20 to 50 times).

## Tests

- All four test files above: 14 tests.
- Run them several times: concurrency bugs are rare by nature (`for i in $(seq 20); do cargo test --test b_plus_tree_concurrent_test || break; done`).

## Notes

**What was changed from the C++ originals.** `GetValue(key, &result)` returning a bool becomes `get_value(&key) -> Vec<V>`; the iterator loop `for (it = Begin(); it != End(); ++it)` becomes `for (key, rid) in tree.begin()`; `LaunchParallelTest` becomes `thread::scope`; `std::shuffle` becomes a seeded shuffle. The tombstone variants of the tests (`NumTombs = 3`, `SequentialEdgeMixTest<2>`) belong to module 2d and run on the plain tree here.

**Utilities.** `tests/b_plus_tree_utils/mod.rs` is BusTub's `b_plus_tree_utils.h` (`IsTreeValid`, `TreeValuesMatch`, `IndexLeaves`, `GetNumLeaves`) plus this course's structure checker, `check_structure`, which verifies every rule at once: uniform depth, sizes within bounds, ordering, key ranges and the leaf chain. Call it from your own tests after every operation while debugging; it names the rule that broke.

**Debugging a failure in the concurrent tests.** Reduce the thread count to 1 first (if it fails there, it is a logic bug in one of stages 3 to 8, not a latching bug). Then run with 2 threads and `RUST_TEST_THREADS=1`. A hang is a deadlock: attach with `gdb`/`lldb`, `thread apply all bt`, and look for two threads each holding a page and waiting for another.

## In BusTub

`test/storage/b_plus_tree_insert_test.cpp`, `b_plus_tree_delete_test.cpp`, `b_plus_tree_sequential_scale_test.cpp` and `b_plus_tree_concurrent_test.cpp`, with `test/include/storage/b_plus_tree_utils.h`. Each C++ test is `DISABLED_` in the starter repository; the autograder enables them.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TEST(BPlusTreeTests, DISABLED_BasicInsertTest)` | `#[test] fn basic_insert_test()` |
| `ASSERT_EQ(a, b)` / `EXPECT_EQ` | `assert_eq!(a, b)` |
| `delete bpm;` at the end of the test | the pool drops at the end of the scope |
| `std::thread` vector joined by hand | `thread::scope(|scope| ...)` |

## Learn more
- [BusTub's tests](https://github.com/cmu-db/bustub/tree/master/test/storage) · [`cargo test` filtering](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

## Performance

Run the concurrent tests in release mode (`cargo test --release --test b_plus_tree_concurrent_test`) and watch the time: with crabbing they take a couple of seconds; with every writer holding the whole path they are several times slower on a multicore machine. The scale test (5,000 keys: a tree 11 levels high) is the one to profile: it spends its time in `child_for` and page latching, not in I/O.

**Measure it.** Time `basic_scale_test` and report operations per second; then raise `scale` to 100,000 with the default leaf and internal sizes and compare: the work per insert should drop by orders of magnitude as the height falls from 11 to 3.

## Hints

### The insert and delete tests with tiny pages

Sizes 2 and 3 exercise every branch: leaves with one key, internal pages with two or three children, splits and merges on almost every operation. If `basic_scale_test` fails with a panic about a full pool, a path holds more pins than the pool has frames (30): a guard that should have been dropped before the next `read_page`.

### The optimistic tests count latches, not time

`optimistic_insert_test` finds a leaf with room, inserts into it, and expects `writes == 1` and `reads > 0`. If the count is higher, find which operation latched a second page for writing: usually the header or the parent, taken before the optimism was attempted.

### The concurrent tests compare against sets of keys, not against a schedule

They cannot know the order in which threads ran, so they check that nothing was lost (`mix_test_2`: the keys no thread touches are still there), nothing was duplicated, and the final contents are exactly the expected set. Reproduce a failure by printing the keys that went missing, then look at what operation could have dropped a key: a split that copied the wrong half, or a merge that lost the right sibling's pairs.
