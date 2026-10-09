BusTub's own trie tests, ported: the 23 333-key mixed workload that checks three versions of the trie at once (before the overrides, after them, after the removals), the copy-on-write tests with the empty key, the store's mixed test, pointer stability and non-copyable values.

## The task

Make the stage's tests pass: `cargo test --test stages_0a s0a_05`.

## Tests

- `s0a_05_mixed_test`: 23 333 puts, then overrides of every second key, then removals of every third; every version is verified at the end.
- `s0a_05_copy_on_write_tests_with_the_empty_key`.
- `s0a_05_trie_store_mixed_test`: the same workload through the store.
- `s0a_05_pointer_stability_and_noncopyable_values`.

## Notes

**What the mixed test proves.** `trie_full`, `trie_override` and `trie_final` are three live versions of one history. If any `put` or `remove` modified a shared node, an earlier version would show the later change. A failure names the key and the version: that tells you whether the bug is in `put` (an override leaked into `trie_full`) or `remove` (a removal leaked into `trie_override`).

**Time.** 23 333 puts of 5-character keys create about 120 000 nodes; the test takes a fraction of a second in release mode and a couple of seconds in debug.

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

## Performance

The workload is dominated by path copying: each put allocates a handful of nodes. Release mode is about 20 times faster than debug here.

**Measure it.** `cargo test --release --test stages_0a s0a_05 -- --nocapture`.

## Hints

### Find which version is wrong

The failing assertion names the version (`full`, `overridden`, `fin`). The version that shows a *later* change is the one that was mutated: look for a place that edits a node through shared access.

### Pruning shows up here

If `fin` still finds a removed key, or a later `put` finds stale children, check that `remove` drops empty nodes.
