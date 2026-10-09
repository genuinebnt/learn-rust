---
title: Count-min sketch: counting a stream in fixed memory
summary: How d hash functions and a d × w matrix of counters estimate how often each item occurred, why the estimate is never too low, how sketches merge, and how top-k works when the sketch itself forgets the items.
minutes: 7
---
You are watching a stream of events (page views, queries, packets) and want to know **how many times each item occurred**, with far too many distinct items to keep a counter for each. A **count-min sketch** answers with a small error and a fixed amount of memory.

It is a matrix of counters, `depth` rows by `width` columns, and one hash function per row. To **add** an item, hash it with each row's function (`hash_r(item) % width`) and add one to that counter in that row. To **estimate** its count, look at its counter in every row and take the **minimum**.

```svg
caption: Three rows, width 6. "apple" was added 5 times and "pear" 2 times. "pear" collides with "apple" in row 0 (counter 7) but not in rows 1 and 2, so its minimum is the true 2.
<svg viewBox="0 0 760 190" role="img" aria-label="A 3 by 6 matrix of counters with two items hashed into it">
<text class="dim sm" x="20" y="50">row 0</text><text class="dim sm" x="20" y="100">row 1</text><text class="dim sm" x="20" y="150">row 2</text>
<g class="mid fg sm">
<rect class="box" x="90" y="30" width="90" height="30"/><rect class="box" x="190" y="30" width="90" height="30"/><rect class="hot" x="290" y="30" width="90" height="30"/><rect class="box" x="390" y="30" width="90" height="30"/><rect class="box" x="490" y="30" width="90" height="30"/><rect class="box" x="590" y="30" width="90" height="30"/>
<text x="135" y="50">0</text><text x="235" y="50">0</text><text x="335" y="50">7</text><text x="435" y="50">0</text><text x="535" y="50">0</text><text x="635" y="50">0</text>
<rect class="box" x="90" y="80" width="90" height="30"/><rect class="hot" x="190" y="80" width="90" height="30"/><rect class="box" x="290" y="80" width="90" height="30"/><rect class="live" x="390" y="80" width="90" height="30"/><rect class="box" x="490" y="80" width="90" height="30"/><rect class="box" x="590" y="80" width="90" height="30"/>
<text x="135" y="100">0</text><text x="235" y="100">5</text><text x="335" y="100">0</text><text x="435" y="100">2</text><text x="535" y="100">0</text><text x="635" y="100">0</text>
<rect class="box" x="90" y="130" width="90" height="30"/><rect class="box" x="190" y="130" width="90" height="30"/><rect class="box" x="290" y="130" width="90" height="30"/><rect class="box" x="390" y="130" width="90" height="30"/><rect class="live" x="490" y="130" width="90" height="30"/><rect class="hot" x="590" y="130" width="90" height="30"/>
<text x="135" y="150">0</text><text x="235" y="150">0</text><text x="335" y="150">0</text><text x="435" y="150">0</text><text x="535" y="150">2</text><text x="635" y="150">5</text>
</g>
<text class="dim sm" x="380" y="182" style="text-anchor:middle">apple: 7, 5, 5 → min 5.  pear: 7, 2, 2 → min 2.</text>
</svg>
```

## Why the minimum

A counter is shared by every item that hashes to it, so each counter is **at least** the item's true count; collisions only add. The minimum over independent rows is the counter with the least interference. The estimate is therefore never too low; it is too high only if the item collides with other items in *every* row. Wider matrices make a collision in one row less likely (error shrinks like `1/width`); more rows make a collision in all rows less likely (the chance shrinks exponentially in `depth`). A `width` of `e/ε` and a `depth` of `ln(1/δ)` give error at most `ε × (total adds)` with probability `1 - δ`.

## Merging

Two sketches with the same dimensions and the same hash functions describe two streams. Adding their matrices element by element gives the sketch of the combined stream. That makes sketches easy to compute in parallel or on many machines and combine at the end. (Sketches with different dimensions use different columns for the same item and cannot be merged.)

## Concurrency

Adding is `depth` independent increments, so each counter can be an atomic integer: threads add at once without a lock, and the totals are exact because `fetch_add` loses no update.

## Top-k: the sketch has no keys

A sketch counts but does not remember *which* items it saw. To find the most frequent items you need candidates from somewhere else (a list of known items, or a heap kept next to the sketch while streaming). `top_k(k, candidates)` estimates each candidate and returns the `k` highest, in descending order.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::vector<std::vector<std::atomic<uint32_t>>>` or a mutex | `Vec<AtomicU32>` of length `depth × width`, indexed `row × width + column` |
| `std::hash<KeyType>` combined with a seed | `DefaultHasher` fed the seed and then the item (deterministic within a build) |
| constructor throws `std::invalid_argument` | `new` returns `Err` for a zero width or depth |

**Port rule:** a matrix of counters shared across threads is a flat `Vec<AtomicU32>`, not a nested vector of locks.

## In real code

### Using it: a sketch with atomic counters

```rust test
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::atomic::{AtomicU32, Ordering};

struct Sketch {
    width: usize,
    depth: usize,
    cells: Vec<AtomicU32>,
}

impl Sketch {
    fn new(width: usize, depth: usize) -> Sketch {
        Sketch { width, depth, cells: (0..width * depth).map(|_| AtomicU32::new(0)).collect() }
    }
    fn cell(&self, row: usize, item: &str) -> &AtomicU32 {
        let mut h = DefaultHasher::new();
        (row as u64, item).hash(&mut h);
        &self.cells[row * self.width + (h.finish() % self.width as u64) as usize]
    }
    fn add(&self, item: &str) {
        for row in 0..self.depth {
            self.cell(row, item).fetch_add(1, Ordering::Relaxed);
        }
    }
    fn count(&self, item: &str) -> u32 {
        (0..self.depth).map(|r| self.cell(r, item).load(Ordering::Relaxed)).min().unwrap()
    }
}

#[test]
fn counts_are_exact_when_nothing_collides_and_never_too_low_when_something_does() {
    let s = Sketch::new(64, 4);
    for _ in 0..5 {
        s.add("apple");
    }
    for _ in 0..2 {
        s.add("pear");
    }
    assert!(s.count("apple") >= 5 && s.count("pear") >= 2);
    assert_eq!(s.count("never seen"), 0);
    let tiny = Sketch::new(1, 3);
    tiny.add("a");
    tiny.add("b");
    assert_eq!((tiny.count("a"), tiny.count("zzz")), (2, 2), "width 1: everything collides");
}

#[test]
fn eight_threads_lose_no_increment() {
    let s = std::sync::Arc::new(Sketch::new(100, 5));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let s = s.clone();
            std::thread::spawn(move || (0..1000).for_each(|_| s.add("hot")))
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(s.count("hot"), 8000);
}
```

### Using it: merging and top-k

```rust test
use std::collections::HashMap;

/// A one-row "sketch" over small integers, to show the shape of merge and top-k: counters add, candidates are ranked.
fn merge(a: &mut [u32], b: &[u32]) {
    assert_eq!(a.len(), b.len(), "different widths cannot be merged");
    for (x, y) in a.iter_mut().zip(b) {
        *x += y;
    }
}

fn top_k(counts: &HashMap<&'static str, u32>, k: usize, candidates: &[&'static str]) -> Vec<(&'static str, u32)> {
    let mut v: Vec<_> = candidates.iter().map(|c| (*c, counts.get(c).copied().unwrap_or(0))).collect();
    v.sort_by(|a, b| b.1.cmp(&a.1)); // stable: ties keep the candidate order
    v.truncate(k);
    v
}

#[test]
fn merging_adds_counter_by_counter() {
    let mut a = vec![1, 0, 3];
    merge(&mut a, &[2, 2, 0]);
    assert_eq!(a, vec![3, 2, 3]);
}

#[test]
fn top_k_ranks_the_candidates_it_is_given() {
    let counts: HashMap<_, _> = [("a", 5), ("b", 9), ("c", 9), ("d", 1)].into_iter().collect();
    assert_eq!(top_k(&counts, 2, &["a", "b", "c", "d"]), vec![("b", 9), ("c", 9)]);
    assert_eq!(top_k(&counts, 10, &["d", "zz"]).len(), 2);
}
```

### In the exercises

- **0d-01:** `CountMinSketch::new`, `insert`, `count`.
- **0d-02:** `clear`, `merge`, `top_k`.

### Where it is used

- **Network monitoring** and **heavy-hitter detection**: finding the busiest flows or queries without per-flow state.
- **Databases** use sketches for cardinality and frequency statistics for query planning (Redis ships a count-min sketch module; Apache DataSketches and Spark have implementations).
- **Cormode and Muthukrishnan**, "An improved data stream summary: the count-min sketch and its applications" (2005), is the original.
