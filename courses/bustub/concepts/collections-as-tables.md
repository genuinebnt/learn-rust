---
title: HashMap, Vec and BTreeMap as page tables and free lists
summary: The three std collections this course builds on, their costs and guarantees, and the places they differ from unordered_map, vector and map.
minutes: 9
---
Every module from the disk manager to the buffer pool and the hash table keeps a *table*: page id to slot, page id to frame, frame to node. Rust gives you three collections for that, and each has a property that differs from its C++ twin in a way that matters for correctness, not only speed.

## At a glance

| need | Rust | C++ | lookup | insert | order | notes |
|---|---|---|---|---|---|---|
| key → value, unordered | `HashMap<K, V>` | `std::unordered_map` | O(1) average | O(1) average | none, and it changes between runs | `K: Hash + Eq` |
| key → value, sorted | `BTreeMap<K, V>` | `std::map` (a red-black tree) | O(log n) | O(log n) | sorted by `K: Ord`; range queries | cache-friendly: nodes hold many keys |
| a growable array, a stack | `Vec<T>` | `std::vector` | O(1) by index | O(1) amortised at the end | insertion order | `pop()` / `push()` make it a stack |
| a queue | `VecDeque<T>` | `std::deque` | O(1) by index | O(1) at both ends | insertion order | a ring buffer |

## HashMap: what to know

```rust
let mut pages: HashMap<PageId, usize> = HashMap::new();
pages.insert(PageId(1000), 0);                      // returns the old value, if any
let slot: Option<&usize> = pages.get(&PageId(1000)); // a borrow: no copy, no insertion
if let Some(s) = pages.remove(&PageId(1000)) { /* ... */ }
*pages.entry(PageId(7)).or_insert(0) += 1;          // one lookup instead of "contains, then insert"
```

- **`get` never inserts.** C++'s `operator[]` inserts a default value when the key is missing, which silently grows the map and turns `if (m[k])` into a mutation. Rust has no `operator[]` for insertion; reading with `map[&k]` panics if the key is absent.
- **The hasher is SipHash by default**, chosen to resist hash-flooding attacks, which makes it slower than `std::hash` on small integer keys. For `PageId(i32)` keys in a hot path you can swap in a faster hasher; for this course the default is right.
- **Iteration order is unspecified and differs between runs** (the hasher is randomly seeded per map). A test that depends on `for (k, v) in &map` order is wrong; sort first, or use a `BTreeMap`.
- **References cannot dangle.** In C++ an iterator into an `unordered_map` is invalidated by a rehash, and a stale one is undefined behaviour. In Rust, `get` returns a borrow, and the borrow checker refuses to let you insert (which may rehash) while it is alive.

## Vec as a stack, and the swap-remove trick

A free list is a stack of slot numbers: `free_slots.push(slot)` to free one, `free_slots.pop()` to take the newest. Both are O(1) amortised: the `Vec` doubles its capacity when full, exactly like the file in the disk manager.

Removing from the *middle* of a `Vec` is O(n) because everything after it shifts. If order does not matter, `swap_remove(i)` is O(1): it moves the last element into the hole. (`VecDeque` gives O(1) at both ends if you need a queue.)

```rust
let slot = free_slots.pop();             // newest first (LIFO): what BusTub does
let slot = free_slots.remove(0);         // O(n): shifts everything: the wrong tool for a queue
let slot = free_queue.pop_front();       // VecDeque: O(1) FIFO
```

## BTreeMap: when you need order

A `BTreeMap` keeps keys sorted, so `range(a..b)` walks a key interval and `first_key_value()` / `pop_first()` give the minimum in O(log n). That is what an *ordered* free list (lowest slot first) or an LRU-K history keyed by timestamp needs, and the reason module 1d's O(log n) eviction uses one. Note it is a B-tree: the same family of structure you build by hand in module 2c, which is why a std `BTreeMap` makes a good test oracle for your B+ tree.

> [!TIP] A collection as a test oracle
> To test a structure you wrote (a replacer, a hash table, a B+ tree), apply the same random operations to it and to a `HashMap` or `BTreeMap` and compare after every step. The std type is slow to reason about but obviously correct; yours is fast and might not be. Module 1d's stages do exactly this.

## Choosing, in one question

> Do I need the keys **sorted** or the **minimum**? `BTreeMap`. Do I need only **lookup by key**? `HashMap`. Do I need **the newest or oldest** thing? `Vec` (stack) or `VecDeque` (queue). Am I scanning all of it anyway, and is it small? A plain `Vec` of pairs beats both.
