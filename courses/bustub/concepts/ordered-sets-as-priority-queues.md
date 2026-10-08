---
title: Ordered sets as priority queues: evicting in O(log n)
summary: Why BinaryHeap cannot do the job, how a BTreeSet of tuple keys gives min, insert and arbitrary remove in O(log n), and the update protocol that keeps the set and the nodes in step.
minutes: 8
---
The first LRU-K `evict` scans every frame to find the minimum: O(n). With a hundred thousand frames and an eviction per page fault, that scan is the whole cost. The fix is to keep the evictable frames in an order so the best victim is always at one end.

## What the structure must do

| operation | when |
|---|---|
| **insert** a frame | it becomes evictable |
| **remove** an arbitrary frame | it is pinned again, accessed (its key changes), or removed |
| **take the minimum** | evict |

All three should be O(log n). `BinaryHeap` gives insert and pop-max but has **no remove-by-value** (and is a max-heap), so the usual workaround is *lazy deletion*: leave stale entries in and skip them when they surface, which makes the size and the memory harder to reason about. A balanced tree does all three directly.

## `BTreeSet<(u8, usize, FrameId)>`

```rust
order: BTreeSet<(u8, usize, FrameId)>,     // the evictable frames, smallest key = next victim

let victim = self.order.first()?.2;         // O(log n): the leftmost element
self.order.insert(key);                      // O(log n)
self.order.remove(&key);                     // O(log n): by value
```

Why the key is a tuple: a tuple of `Ord` types is itself `Ord`, compared **lexicographically**. `(0, first_access, frame)` sorts before every `(1, kth_access, frame)`, so frames with infinite distance come first, oldest first access first, with the frame id as a final tie-break that makes keys unique (a set holds each key once; two frames must not collide).

| C++ | Rust |
|---|---|
| `std::set<std::tuple<int, size_t, frame_id_t>>` | `BTreeSet<(u8, usize, FrameId)>` |
| `*s.begin()` | `s.first()` (Rust 1.66+) / `s.iter().next()` |
| `s.erase(s.begin())` | `s.pop_first()` |
| `std::priority_queue` (no erase) | `BinaryHeap` (no remove) |
| `std::set` is a red-black tree | `BTreeSet` is a B-tree: fewer allocations, better cache use |

## The update protocol: remove old, change, insert new

The set stores *keys computed from node state*. When the state changes, the key changes, and the set must be told in the right order:

```rust
if node.is_evictable { self.order.remove(&eviction_key(node)); }   // 1. remove the entry under the OLD key
node.record(now);                                                   // 2. change the node
if node.is_evictable { self.order.insert(eviction_key(node)); }    // 3. insert under the NEW key
```

> [!WARNING] The stale entry
> Mutate first and call `remove(&eviction_key(node))` after, and you remove *nothing* (the new key is not in the set) and leave the old entry behind: the set now contains a key that matches no node, and a later `evict` returns a frame whose history says otherwise. This is the most common bug in this stage. The invariant to assert in tests: **the set contains exactly the evictable frames, each under the key its current state produces.**

## When a tree is the wrong tool

A `BTreeSet` pays O(log n) and allocates nodes. If you only ever need the minimum and never remove arbitrary elements, `BinaryHeap` is smaller and faster. If the keys are small integers in a known range, a bucket array or a bitmap with a "find first set" instruction is O(1). Choosing is the lesson; the tests check behaviour and speed, not which you picked.
