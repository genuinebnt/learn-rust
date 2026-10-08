Evicting by scanning every frame is fast enough for a hundred frames and hopeless for a hundred thousand. This stage makes `evict` **O(log n)** by keeping the evictable frames in an ordered set, so the next victim is always the first element. The ordering key from the previous stage is the same; what changes is that the set must be **kept in step with the nodes** on every access and every change of evictability.

The model test from the previous stage becomes your safety net: random operations applied to both versions must pick the same victims.

**Where this fits.** Scanning every frame per eviction is O(n). A buffer pool evicts on nearly every miss, so with a million frames that is a million steps per page fault.

## The task

Make `evict()` cost `O(log n)` in `src/buffer/lru_k_replacer.rs`. The suggested design (change it freely): keep a `BTreeSet<(u8, usize, FrameId)>` of the **evictable** frames, sorted so the next victim is `first()`. The key is the same tuple as stage 6, plus the frame id so two frames never collide. Every operation that changes a frame's key or its evictable flag must update the set: `record_access` (remove the old key, record, insert the new one), `set_evictable`, `evict` and `remove`.

## Tests

- 100,000 frames, one access each: all become evictable, then are evicted in order, within **5 seconds** (a scan takes minutes). 50,000 frames get a second access *after* becoming evictable (their keys change): still evicted in order, still fast.
- Frames toggled not-evictable and back keep their place. (All the earlier stages' tests, including the model test, must still pass.).

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

## Performance

Each `record_access`, `set_evictable`, `evict` and `remove` now does O(1) hash work plus **O(log n)** set work (a `BTreeSet` insert, remove or `first()`). For 100 000 frames that is about 17 comparisons per operation instead of 100 000: the 100 000-eviction test drops from tens of seconds to well under one. A `BTreeSet` stores keys in wide nodes, so those comparisons touch a handful of cache lines rather than chasing a pointer per level as a red-black tree does.

The price is **memory** (a second copy of each evictable frame's key) and a **bookkeeping obligation**: every state change must update both the node and the set. The speed-up is real only if the update protocol is right, which is what the model test checks.

**Measure it.** Evict 100 000 frames and time it; then double to 200 000 and confirm the time roughly doubles (n log n), not quadruples (n squared). Compare `BTreeSet<(u8, usize, FrameId)>` against a `BinaryHeap` with lazy deletion for this workload and note which one your `remove` and `set_evictable` can use directly.

## Hints

### Remove under the old key, then change, then insert under the new

The set stores keys *derived from node state*. If you change the node first, the old key can no longer be recomputed, `remove` finds nothing, and the stale entry stays in the set forever: a later `evict` returns a frame whose history disagrees with its key. The protocol is: **remove (old key) → mutate → insert (new key)**, and only for frames that are evictable at that moment. Wrap it in one helper so every mutation goes through it.

### The key must be unique and total

A `BTreeSet` holds each key once and orders them by `Ord`. Two different frames with the same `(class, timestamp)` would collide and one would silently vanish, so the frame id is the **last tuple element**: it breaks every tie and makes keys unique. Check the inputs that produce equal timestamps: after `remove` and a fresh access a frame restarts its history; a frame with exactly K accesses and one with more may share a K-th timestamp.

### Two representations, one truth: check it

You now have `node_store` (the nodes) and `order` (the sorted evictable keys). The invariant: *`order` contains exactly one key per evictable node, equal to what `eviction_key(node)` returns now.* A `check()` that rebuilds the set from the nodes and compares costs O(n log n), so call it only in tests and `debug_assert!`. The random model test, run for several values of K, is what will find the case you did not think of.
