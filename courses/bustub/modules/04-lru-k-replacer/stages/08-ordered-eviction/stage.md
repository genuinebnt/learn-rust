**Where this fits.** Scanning every frame per eviction is O(n). A buffer pool evicts on nearly every miss, so with a million frames that is a million steps per page fault.

## The task

Make `evict()` cost `O(log n)` in `src/buffer/lru_k_replacer.rs`. The suggested design (change it freely): keep a `BTreeSet<(u8, usize, FrameId)>` of the **evictable** frames, sorted so the next victim is `first()`. The key is the same tuple as stage 6, plus the frame id so two frames never collide. Every operation that changes a frame's key or its evictable flag must update the set: `record_access` (remove the old key, record, insert the new one), `set_evictable`, `evict` and `remove`.

## Tests

- 100,000 frames, one access each: all become evictable, then are evicted in order, within **5 seconds** (a scan takes minutes).
- 50,000 frames get a second access *after* becoming evictable (their keys change): still evicted in order, still fast.
- Frames toggled not-evictable and back keep their place. (All the earlier stages' tests, including the model test, must still pass.)

## Syntax and methods

```rust
use std::collections::BTreeSet;
let mut order: BTreeSet<(u8, usize, FrameId)> = BTreeSet::new();
order.insert(key);  order.remove(&key);   // O(log n); remove needs the *current* key, so compute it before you change the node
order.first()                              // Option<&T>: the smallest element (stable since Rust 1.66)
order.pop_first()                          // remove and return the smallest
```

## Notes

**The invariant.** The set must hold exactly the evictable frames, each under its *current* key. The easy bug is changing a node and *then* trying to remove its old key (which you can no longer compute). Remove first, change, insert. A `debug_assert!` that compares the set's size to `curr_size` after each operation will find most mistakes.

`BTreeSet` is an ordered set (a B-tree: the same family as the database indexes you build in the Index module). Rust has no built-in priority queue with `decrease-key`; "remove old entry, insert new" on an ordered set is the standard substitute (and what BusTub leaderboard solutions do with `std::set`).

## In BusTub

BusTub's reference keeps `std::list`s and scans. The leaderboard rewards an O(log n) `Evict`, typically with a `std::set` ordered by `(is_finite, timestamp)`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::set<std::tuple<int, size_t, frame_id_t>>`, `*set.begin()`, `set.erase(set.begin())` | `BTreeSet<(u8, usize, FrameId)>`, `first()`, `pop_first()` |
| `std::set` is a red-black tree; `std::unordered_set` a hash table | `BTreeSet` is a B-tree; `HashSet` a hash table |
| `std::priority_queue`: no removal of arbitrary elements | `BinaryHeap`: the same limitation; use `BTreeSet` or lazy deletion |
| mutating a key in place inside a `std::set` is undefined behaviour | `BTreeSet` gives only `&T`: you must remove and reinsert |

**Port rule:** a C++ `std::set`/`std::map` used as an ordered index becomes `BTreeSet`/`BTreeMap`. If you need "update the priority of X", it is remove + insert.

## Learn more
- [`BTreeSet`](https://doc.rust-lang.org/std/collections/struct.BTreeSet.html) · [`BTreeMap`](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) · C++ [`std::set`](https://en.cppreference.com/w/cpp/container/set)
- [`moka`](https://github.com/moka-rs/moka) and [`lru-rs`](https://github.com/jeromefroe/lru-rs): production caches in Rust · InnoDB's buffer pool uses a segmented LRU (young/old sublists) for the same scan-resistance goal
