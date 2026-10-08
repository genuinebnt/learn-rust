**Where this fits.** The last piece of remove.

## The task

At the end of `merge_empty_buckets` in `src/container/disk/hash/disk_extendible_hash_table.rs`: while the directory `can_shrink()`, `decr_global_depth()`.

## Tests

- A table emptied completely returns to global depth 0. After removing three quarters of 64 keys the depth is **lower** (the directory shrank *as buckets merged*, not only at the very end) and the survivors are still there.
- A directory that can't shrink keeps its depth. **A model test**: 2000 random inserts and removes against a `HashMap`, checking `insert`'s and `remove`'s result at every step and `verify_integrity` every 100 steps.

## Syntax and methods

```rust
while directory.can_shrink() { directory.decr_global_depth(); }
```

## Notes

**The model test is the real safety net.** The table has so many interacting cases (split with and without growth, merge with and without shrink, cascades) that hand-written examples can't cover them. A random workload against a trivially correct model (`HashMap`) plus the page-level invariant checker finds the rest. This is *property-based testing*, and it works on every data structure in this course: B+ trees next.

## In BusTub

The spec: "Shrink the directory if possible: while `CanShrink()`, `DecrGlobalDepth()`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `while (dir->CanShrink()) { dir->DecrGlobalDepth(); }` | the same |
| `std::unordered_map<K, V>` as the reference model in tests | `HashMap<K, V>` |
| `rand()` seeded by time: failures you can't reproduce | a fixed-seed LCG: every failure is replayable |

## Learn more
- [Property-based testing](https://en.wikipedia.org/wiki/Software_testing#Property_testing) · the [`proptest`](https://docs.rs/proptest) crate (shrinks failing inputs automatically) · [`quickcheck`](https://docs.rs/quickcheck)
