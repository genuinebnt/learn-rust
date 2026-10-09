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

## In real code

### The API you will use

| type | call | what it does |
|---|---|---|
| `HashMap<K, V>` | `insert(k, v)` | returns the old value, if any |
| | `get(&k)` / `get_mut(&k)` | `Option<&V>` / `Option<&mut V>`: never inserts |
| | `entry(k).or_insert(v)` / `.or_insert_with(f)` / `.or_default()` | **one lookup** for "get or create" |
| | `remove(&k)` / `contains_key(&k)` / `len()` | |
| `Vec<T>` | `push(x)` / `pop()` | a stack: the free list |
| | `swap_remove(i)` | O(1) removal when order does not matter |
| | `insert(i, x)` / `remove(i)` | O(n): shifts the tail |
| `VecDeque<T>` | `push_back` / `pop_front` / `push_front` / `pop_back` | a queue, O(1) at both ends |
| `BTreeMap` / `BTreeSet` | `range(a..b)` / `first_key_value()` / `pop_first()` | ordered access |

```rust test
use std::collections::HashMap;

#[test]
fn page_table_with_the_entry_api() {
    let mut page_table: HashMap<u32, usize> = HashMap::new();
    let mut free: Vec<usize> = vec![2, 1, 0];                 // a stack: pop() hands out 0 first

    for page in [10, 20, 10] {
        let frame = *page_table.entry(page).or_insert_with(|| free.pop().expect("a free frame"));
        println!("page {page} -> frame {frame}");
    }
    assert_eq!(page_table[&10], 0);
    assert_eq!(page_table[&20], 1);
    assert_eq!(free, vec![2]);                                 // page 10 was already mapped: no frame was taken the second time
    assert_eq!(page_table.get(&99), None);                     // get never inserts
}
```

```rust test
use std::collections::{BTreeMap, BTreeSet, VecDeque};

#[test]
fn the_right_collection_for_the_question() {
    // Do I need the smallest key? BTreeSet::first / pop_first
    let mut by_age: BTreeSet<(u32, usize)> = BTreeSet::new();      // (timestamp, frame)
    by_age.insert((5, 2));
    by_age.insert((3, 7));
    by_age.insert((9, 1));
    assert_eq!(by_age.pop_first(), Some((3, 7)));

    // Do I need a key range? BTreeMap::range
    let slots: BTreeMap<u32, &str> = [(1, "a"), (5, "b"), (9, "c")].into_iter().collect();
    let keys: Vec<_> = slots.range(2..=9).map(|(k, _)| *k).collect();
    assert_eq!(keys, vec![5, 9]);

    // Do I need the oldest item? VecDeque
    let mut q: VecDeque<u32> = VecDeque::new();
    q.push_back(1);
    q.push_back(2);
    assert_eq!(q.pop_front(), Some(1));
}
```

```rust test
#[test]
fn vec_as_a_free_list_and_swap_remove() {
    let mut free_slots: Vec<usize> = Vec::new();
    free_slots.push(4);                         // slot 4 was freed
    free_slots.push(9);                         // then slot 9
    assert_eq!(free_slots.pop(), Some(9));      // newest first (LIFO): what BusTub does

    let mut v = vec!['a', 'b', 'c', 'd'];
    assert_eq!(v.swap_remove(1), 'b');          // O(1): the last element fills the hole
    assert_eq!(v, vec!['a', 'd', 'c']);         // order changed: fine for a set, wrong for a queue
}
```

### In the exercises

- **1a-01 and 1a-02:** a disk manager must remember where each page lives and which space is free again. A map from page id to place and a stack of freed places is the usual design, and `HashMap::entry`-style code (look up, else allocate and record) is the usual shape; a design with no free list is a valid first attempt that 1a-02's file-size property will reject.
- **1c-01 and 1c-02:** the arena's free list is a `Vec<usize>` stack, and the LRU replacer's `frame -> handle` map is a `HashMap`. Use `remove(&frame)` to take the handle out in the same call that you use it.
- **1d-01:** each frame's history is a `VecDeque<usize>`: `push_back` the new timestamp, `pop_front` when it holds more than K.
- **1d-03 (later):** the evictable frames go in a `BTreeSet`; `first()` is the next victim (second example).

### Where it is used

- **Every cache, session table and catalog**: `HashMap` keyed by id in front of a slower store.
- **Ordered indexes**: a `BTreeMap` is a B-tree, the same family as the index you build in module 2c; it is also a good *oracle* to test your own index against.
- **Schedulers and timers**: a `BTreeMap<Instant, Task>` pops the next due task with `pop_first`; a `VecDeque` is the run queue of most executors.
- **Free lists and arenas**: `Vec` as a stack is how allocators and slab pools recycle slots.
