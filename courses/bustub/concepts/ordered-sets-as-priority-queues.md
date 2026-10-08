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

## In real code

### Using it: the API and the three ways to get a minimum

```rust test
use std::collections::BTreeSet;
use std::ops::Bound::{Excluded, Unbounded};

#[test]
fn btreeset_as_an_ordered_pool() {
    let mut s: BTreeSet<(u8, usize, u32)> = BTreeSet::new();
    assert!(s.insert((1, 5, 7)));                      // insert returns true when the key was new
    assert!(!s.insert((1, 5, 7)));                     // ...and false for a duplicate: a set holds each key once
    s.insert((0, 9, 2));
    s.insert((1, 3, 4));
    assert_eq!(s.first(), Some(&(0, 9, 2)));           // tuples compare field by field: the 0 sorts before every 1
    assert_eq!(s.last(), Some(&(1, 5, 7)));
    assert!(s.remove(&(1, 3, 4)));                     // remove by VALUE: true if it was there
    assert!(!s.remove(&(1, 3, 4)));
    assert_eq!(s.iter().next(), s.first());            // iteration is in sorted order
    let after_first: Vec<_> = s.range((Excluded((0, 9, 2)), Unbounded)).collect();   // everything after a key
    assert_eq!(after_first, vec![&(1, 5, 7)]);
    assert_eq!(s.pop_first(), Some((0, 9, 2)));        // take the minimum
    assert_eq!(s.len(), 1);
}

#[test]
fn the_update_protocol_and_the_stale_entry_bug() {
    // a "node" is just (state), the key is computed from it
    let key = |state: usize, fid: u32| (1u8, state, fid);

    // right: remove under the old key, mutate, insert under the new one
    let mut set = BTreeSet::new();
    let mut state = 10;
    set.insert(key(state, 1));
    assert!(set.remove(&key(state, 1)));
    state = 20;
    set.insert(key(state, 1));
    assert_eq!(set.len(), 1);
    assert_eq!(set.first(), Some(&key(20, 1)));

    // wrong: mutate first, remove after. The remove finds nothing and the old entry stays forever.
    let mut set = BTreeSet::new();
    let mut state = 10;
    set.insert(key(state, 1));
    state = 20;
    assert!(!set.remove(&key(state, 1)), "the NEW key is not in the set");
    set.insert(key(state, 1));
    assert_eq!(set.len(), 2, "two entries for one frame: a later evict() can return a frame by a key it no longer has");
}
```

```rust test
use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashSet};

#[test]
fn binary_heap_with_lazy_deletion_is_the_alternative() {
    // BinaryHeap is a max-heap with no remove: wrap in Reverse for min, and "remove" by remembering what is stale.
    let mut heap = BinaryHeap::new();
    let mut removed: HashSet<(usize, u32)> = HashSet::new();
    for (t, f) in [(5, 1), (3, 2), (9, 3), (1, 4)] { heap.push(Reverse((t, f))); }
    removed.insert((1, 4));                                  // "remove" frame 4: just note it
    let mut order = vec![];
    while let Some(Reverse(top)) = heap.pop() {              // stale entries are skipped when they surface
        if removed.remove(&top) { continue; }
        order.push(top);
    }
    assert_eq!(order, vec![(3, 2), (5, 1), (9, 3)]);
    // The cost: len() of the heap is not the number of live entries, and memory holds the stale ones until they surface.
}

#[test]
fn bucket_array_when_keys_are_small_integers() {
    // O(1) min over keys 0..64: a bitmap and a trailing-zeros instruction.
    let mut bits: u64 = 0;
    for k in [41u32, 7, 55] { bits |= 1 << k; }
    assert_eq!(bits.trailing_zeros(), 7);                    // the minimum key
    bits &= !(1 << 7);                                       // remove it
    assert_eq!(bits.trailing_zeros(), 41);
}
```

### In the exercises

- **1d-03 (evict in O(log n)):** the `BTreeSet<(u8, usize, FrameId)>` and key function of the LRU-K concept; `evict` is `pop_first`.
- **The update protocol** applies in `record_access`, `set_evictable` and `remove` of that stage; its model test checks the fast replacer against the simple one.
- **Choosing:** the lazy `BinaryHeap` above works too; the stage's Performance section asks you to compare them, and `size()` is the awkward part (a heap's length counts stale entries).

### Where it is used

- **Schedulers**: Linux's CFS keeps runnable tasks in a red-black tree ordered by virtual runtime and always runs the leftmost (the same shape: min, insert, remove an arbitrary task when it blocks).
- **Timers**: a timer wheel or ordered set of deadlines; `tokio`'s time driver and many event loops pick the earliest deadline this way.
- **Order books and leaderboards**: an ordered set keyed by `(price, time)` gives best bid in O(log n) and cancels in O(log n).
- **Dijkstra with decrease-key**: a `BTreeSet<(dist, node)>` replaces the missing `decrease_key` of `BinaryHeap` with remove-old/insert-new, the same protocol.
