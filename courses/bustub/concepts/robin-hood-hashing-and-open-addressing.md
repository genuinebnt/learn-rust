---
title: Open addressing and Robin Hood hashing
summary: How a hash set stores keys directly in its buckets, probes forward on collisions, evens out probe distances by letting a poorer key take a richer one's place, and what tombstones do to lookups.
minutes: 8
---
A hash table needs a plan for two keys that want the same bucket. **Chaining** hangs a list off each bucket. **Open addressing** keeps everything in one flat array: a key that finds its **home bucket** (`hash % capacity`) taken tries the next one, and the next, until it finds a free bucket. This is *linear probing*. It is cache friendly (neighbouring buckets are neighbours in memory) and has no allocation per key.

Plain linear probing has a weakness: some keys get unlucky and end far from home, and those make some lookups very long. **Robin Hood hashing** evens that out. Each key has a **probe distance** (how far it sits from home). When inserting, if the incoming key is further from its home than the resident of the bucket you are looking at, **swap**: the incoming key takes the bucket and the resident becomes the one that keeps probing. The rich (close to home) give to the poor.

```svg
caption: Capacity 4. Keys a, b, c have home 0; d has home 1. a sits at 0, b at 1, d at 2 (probe distance 1). Inserting c: at bucket 1, b is at distance 1 and c would be too (no swap); at bucket 2, d is at distance 1 and c would be at 2, so c takes bucket 2 and d moves to bucket 3.
<svg viewBox="0 0 760 170" role="img" aria-label="Four buckets before and after a Robin Hood displacement">
<text class="dim sm" x="20" y="30">before</text>
<rect class="live" x="100" y="10" width="110" height="34" rx="3"/><text class="mid fg sm" x="155" y="32">0: a (d=0)</text>
<rect class="live" x="220" y="10" width="110" height="34" rx="3"/><text class="mid fg sm" x="275" y="32">1: b (d=1)</text>
<rect class="live" x="340" y="10" width="110" height="34" rx="3"/><text class="mid fg sm" x="395" y="32">2: d (d=1)</text>
<rect class="box" x="460" y="10" width="110" height="34" rx="3"/><text class="mid dim sm" x="515" y="32">3: empty</text>
<text class="dim sm" x="20" y="110">after put c</text>
<rect class="live" x="100" y="90" width="110" height="34" rx="3"/><text class="mid fg sm" x="155" y="112">0: a (d=0)</text>
<rect class="live" x="220" y="90" width="110" height="34" rx="3"/><text class="mid fg sm" x="275" y="112">1: b (d=1)</text>
<rect class="hot" x="340" y="90" width="110" height="34" rx="3"/><text class="mid fg sm" x="395" y="112">2: c (d=2)</text>
<rect class="hot" x="460" y="90" width="110" height="34" rx="3"/><text class="mid fg sm" x="515" y="112">3: d (d=2)</text>
</svg>
```

## Lookup, and the early exit

To find a key, probe from its home. You can stop at an empty bucket: the key would have been placed there. A textbook Robin Hood table also stops at a resident that is *closer to home than the sought key would be here*, because the sought key would have displaced it. That early exit is why Robin Hood lookups of absent keys are cheap.

## Deleting: tombstones, and the trap

Deleting a key by emptying its bucket would break the chains of keys that probed past it: their lookups would stop at the new hole. Two fixes: *backward-shift* the following keys, or leave a **tombstone**, a marker meaning "a key was here; keep probing, but this bucket is free for an insert". Tombstones are simple and lock-friendly, with a catch:

> **After tombstones, the early exit is unsafe.** A tombstone can be reused by a new key with a short probe distance. A key that was already further along the chain now has, in front of it, a resident that looks "closer to home", and a lookup that stops there never finds it.

So a table with tombstones must probe until an *empty* bucket (or a full lap). The Robin Hood displacement on insert still pays off: it keeps the longest probe short. This course's tests include a model check against `HashSet` that fails if the early exit is kept.

## A fixed-capacity table is full when no bucket is free

With `size` live keys in `capacity` buckets, a free bucket (empty or tombstone) exists exactly when `size < capacity`. Check that **before** displacing anything: an insert that swaps residents and then discovers there is no room has already lost a key.

## Concurrency

A single reader-writer lock around the table is correct and simple: lookups share it, inserts and removes take it exclusively. Finer locking (a lock per stripe of buckets) is faster for independent inserts, but a displacement chain can cross stripes, so it must take them in an order; BusTub's `ParallelSpeedupTest` rewards that, this course's port does not.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::vector<Bucket>` with a `state` enum and a union-ish key | `Vec<Slot<K>>` with `enum Slot<K> { Empty, Tombstone, Live(K) }` |
| `explicit RobinHoodHashSet(size_t capacity)` that throws `std::invalid_argument` | `new(capacity) -> Result<_, Exception>` |
| `std::hash<K>` or a custom functor | a `RobinHoodHash` trait (the same integer multiplier as BusTub's) |
| move constructor that must leave the source "empty" | a Rust move: the old binding simply cannot be used |

**Port rule:** an `enum` with a variant per bucket state replaces a state byte next to a possibly-uninitialised key.

## In real code

### Using it: Robin Hood insertion and lookup

```rust test
#[derive(Clone, PartialEq, Debug)]
enum Slot {
    Empty,
    Live(u32),
}

struct Table {
    slots: Vec<Slot>,
}

impl Table {
    fn home(&self, key: u32) -> usize {
        (key.wrapping_mul(2654435761) as usize) % self.slots.len()
    }
    fn distance(&self, key: u32, at: usize) -> usize {
        (at + self.slots.len() - self.home(key)) % self.slots.len()
    }
    fn insert(&mut self, key: u32) -> bool {
        if self.slots.iter().filter(|s| matches!(s, Slot::Live(_))).count() == self.slots.len() {
            return false;
        }
        let (mut carried, mut at) = (key, self.home(key));
        loop {
            match self.slots[at].clone() {
                Slot::Empty => {
                    self.slots[at] = Slot::Live(carried);
                    return true;
                }
                Slot::Live(resident) => {
                    if self.distance(resident, at) < self.distance(carried, at) {
                        self.slots[at] = Slot::Live(carried);
                        carried = resident;
                    }
                }
            }
            at = (at + 1) % self.slots.len();
        }
    }
    fn contains(&self, key: u32) -> bool {
        let mut at = self.home(key);
        for _ in 0..self.slots.len() {
            match &self.slots[at] {
                Slot::Empty => return false,
                Slot::Live(k) if *k == key => return true,
                _ => {}
            }
            at = (at + 1) % self.slots.len();
        }
        false
    }
}

#[test]
fn inserted_keys_are_found_even_after_displacements() {
    let mut t = Table { slots: vec![Slot::Empty; 16] };
    for k in 0..14 {
        assert!(t.insert(k * 5));
    }
    assert!((0..14).all(|k| t.contains(k * 5)));
    assert!(!t.contains(1) && !t.contains(1000));
}

#[test]
fn a_full_table_refuses_without_losing_a_key() {
    let mut t = Table { slots: vec![Slot::Empty; 4] };
    for k in 0..4 {
        assert!(t.insert(k));
    }
    assert!(!t.insert(99));
    assert!((0..4).all(|k| t.contains(k)), "the failed insert displaced nothing");
}
```

### Using it: the tombstone trap in a few lines

```rust test
#[derive(Clone, Copy, PartialEq, Debug)]
enum S {
    Empty,
    Tomb,
    Live(u32, usize), // key, home
}

fn probe_distance(cap: usize, home: usize, at: usize) -> usize {
    (at + cap - home) % cap
}

/// The textbook lookup with the early exit: stop at a resident closer to home than we would be.
fn contains_with_early_exit(slots: &[S], key: u32, home: usize) -> bool {
    for d in 0..slots.len() {
        let at = (home + d) % slots.len();
        match slots[at] {
            S::Empty => return false,
            S::Tomb => {}
            S::Live(k, h) => {
                if k == key {
                    return true;
                }
                if probe_distance(slots.len(), h, at) < d {
                    return false;
                }
            }
        }
    }
    false
}

fn contains_to_the_end(slots: &[S], key: u32, home: usize) -> bool {
    (0..slots.len()).map(|d| slots[(home + d) % slots.len()]).take_while(|s| *s != S::Empty).any(|s| matches!(s, S::Live(k, _) if k == key))
}

#[test]
fn reusing_a_tombstone_hides_a_key_from_the_early_exit() {
    // x (home 0) sits at bucket 2, behind a tombstone at 1; then y (home 1, distance 0 there) is put into the tombstone's bucket 1
    let slots = [S::Live(10, 0), S::Live(99, 1), S::Live(50, 0), S::Empty];
    // key 50 has home 0 and lives at bucket 2 (distance 2); bucket 1 holds y at distance 0 < 1
    assert!(!contains_with_early_exit(&slots, 50, 0), "the early exit stops in front of y");
    assert!(contains_to_the_end(&slots, 50, 0), "probing to the end finds it");
}

#[test]
fn without_tombstones_the_early_exit_is_fine() {
    let slots = [S::Live(10, 0), S::Live(50, 0), S::Empty, S::Empty];
    assert!(contains_with_early_exit(&slots, 50, 0));
    assert!(!contains_with_early_exit(&slots, 77, 0));
}
```

### In the exercises

- **0c-01:** home buckets and probe distances with wraparound.
- **0c-02:** Robin Hood insert, lookup, and the full-table rule.
- **0c-03:** remove with tombstones, reuse, `max_probe_distance`.
- **0c-04:** BusTub's concurrent tests.

### Where it is used

- **Rust's `HashMap`** (hashbrown) uses open addressing with SIMD group probing (Swiss tables), not Robin Hood; the previous std implementation (before 1.36) used Robin Hood hashing.
- **Abseil's `flat_hash_map`** and **Google's Swiss tables**: open addressing with tombstones (they call them "deleted" markers).
- **Many game and embedded hash tables** pick Robin Hood for its low variance in probe length.
