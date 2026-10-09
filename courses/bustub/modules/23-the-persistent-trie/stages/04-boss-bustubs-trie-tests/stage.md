BusTub's own trie tests, ported: the 23 333-key mixed workload that checks three versions of the trie at once (before the overrides, after them, after the removals), the copy-on-write tests with the empty key, the store's mixed test, pointer stability and non-copyable values.

## The task

Make the stage's tests pass: `cargo test --test stages_0a s0a_05`.

The tests: BusTub's own (the mixed test, copy-on-write with the empty key, the trie-store mixed test, pointer stability and non-copyable values), a new test where **a reader never sees a value go backwards while a writer counts up** (three readers, one writer, three thousand writes, an unrelated key that never changes), and the stage 1 to 3 properties.

## Your freedom

None new: a failure belongs to one of the earlier stages.

## The Rust toolbox

**Reading a failing BusTub test.** The ported tests keep BusTub's names and numbers; the failing line tells you which key and which version; reproduce it with a three-line trie in a `#[test]` of your own.

**Threads that must not deadlock.** If a test hangs, a lock is held across a call that takes it again: print which one in the order the code takes them.

## Design notes

**What the mixed test proves.** `trie_full`, `trie_override` and `trie_final` are three live versions of one history. If any `put` or `remove` modified a shared node, an earlier version would show the later change. A failure names the key and the version: that tells you whether the bug is in `put` (an override leaked into `trie_full`) or `remove` (a removal leaked into `trie_override`).

**Time.** 23 333 puts of 5-character keys create about 120 000 nodes; the test takes a fraction of a second in release mode and a couple of seconds in debug.

## If this is new

- Everything is in the earlier stages of this module.

## Tests

- BusTub's trie tests; the monotonic-read test; the earlier properties.

## Hints

### Find which version is wrong

The failing assertion names the version (`full`, `overridden`, `fin`). The version that shows a *later* change is the one that was mutated: look for a place that edits a node through shared access.

### Pruning shows up here

If `fin` still finds a removed key, or a later `put` finds stale children, check that `remove` drops empty nodes.

## Performance

The tests run in a fraction of a second; the counter test performs three thousand writes while three readers spin.

## Experiment

Optional. Predict first, then run.

1. **Publish before building.** Store the root first and fill it in later. Which test sees a half-built trie?
2. **Longer histories.** Raise the length of the random histories. Does anything change?

## Other designs

None for this stage. The *Other designs* sections of 0a-01 to 0a-03 list the alternatives to compare with yours.

## In BusTub

`test/primer/trie_test.cpp`, `trie_store_test.cpp`, `trie_noncopy_test.cpp` and `trie_store_noncopy_test.cpp`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `fmt::format("{:#05}", i)` | `format!("{i:05}")` |
| `ASSERT_EQ(trie.Get<std::string>(key), nullptr)` | `assert!(trie.get::<String>(&key).is_none())` |

**Port rule:** gtest assertions are `assert!` and `assert_eq!`.

## Learn more

- [BusTub's primer tests](https://github.com/cmu-db/bustub/tree/master/test/primer)
