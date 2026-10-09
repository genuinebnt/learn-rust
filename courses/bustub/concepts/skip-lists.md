---
title: Skip lists: a sorted linked list with express lanes
summary: How random node heights turn a linked list into a structure with logarithmic search, the update vector that insert and erase need, and why a seeded generator gives repeatable shapes.
minutes: 8
---
A sorted linked list finds a key in `O(n)`: you walk from the front. A balanced tree does it in `O(log n)` but needs rebalancing code. A **skip list** gets `O(log n)` on average with a simple trick: give every node a random **height** and link a node of height `h` into `h` lists, one per level. Level 0 is the full sorted list; level 1 links about every other node, level 2 about every fourth, and so on. Higher levels are express lanes.

```svg
caption: Seven keys. A search for 6 starts on the top level, takes the express link 1 → 5 (5 < 6), finds the next link too far, drops a level, goes 5 → 7 ... too far, drops again and finds 6 on level 0.
<svg viewBox="0 0 760 230" role="img" aria-label="A skip list with three levels">
<defs><marker id="sk-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="20" y="40">level 2</text><text class="dim sm" x="20" y="100">level 1</text><text class="dim sm" x="20" y="160">level 0</text>
<rect class="box" x="90" y="25" width="50" height="170" rx="3"/><text class="dim sm" x="115" y="212" style="text-anchor:middle">head</text>
<g><rect class="live" x="200" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="222" y="165">1</text>
<rect class="live" x="270" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="292" y="165">3</text>
<rect class="live" x="340" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="362" y="165">4</text>
<rect class="live" x="410" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="432" y="165">5</text>
<rect class="hot" x="480" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="502" y="165">6</text>
<rect class="live" x="550" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="572" y="165">7</text>
<rect class="live" x="620" y="145" width="44" height="30" rx="3"/><text class="mid fg sm" x="642" y="165">9</text></g>
<rect class="live" x="200" y="85" width="44" height="30" rx="3"/><text class="mid fg sm" x="222" y="105">1</text>
<rect class="live" x="410" y="85" width="44" height="30" rx="3"/><text class="mid fg sm" x="432" y="105">5</text>
<rect class="live" x="550" y="85" width="44" height="30" rx="3"/><text class="mid fg sm" x="572" y="105">7</text>
<rect class="live" x="410" y="25" width="44" height="30" rx="3"/><text class="mid fg sm" x="432" y="45">5</text>
<path class="ln" d="M142 40 L408 40" marker-end="url(#sk-a)"/><path class="ln" d="M142 100 L198 100" marker-end="url(#sk-a)"/><path class="ln" d="M246 100 L408 100" marker-end="url(#sk-a)"/><path class="ln" d="M456 100 L548 100" marker-end="url(#sk-a)"/>
<path class="ln" d="M142 160 L198 160" marker-end="url(#sk-a)"/><path class="ln" d="M246 160 L268 160" marker-end="url(#sk-a)"/><path class="ln" d="M316 160 L338 160" marker-end="url(#sk-a)"/><path class="ln" d="M386 160 L408 160" marker-end="url(#sk-a)"/><path class="ln" d="M456 160 L478 160" marker-end="url(#sk-a)"/><path class="ln" d="M526 160 L548 160" marker-end="url(#sk-a)"/><path class="ln" d="M596 160 L618 160" marker-end="url(#sk-a)"/>
</svg>
```

## Search

Start at the head on the highest level in use. While the next node on this level has a key **before** the sought one, move to it. Then drop one level and repeat. At level 0, the next node is either the key or the first key after it.

## Insert and erase: the update vector

While searching, remember the **last node visited on each level**: the *update vector*. To insert a node of height `h`, for each level below `h` link the new node between `update[level]` and that node's old next. To erase, for each level of the doomed node make `update[level]` point past it. If an insert is taller than the list, the head provides the missing predecessors; if an erase leaves the top levels empty, lower the list's height.

## Random heights

A node's height comes from a coin: height 1; while a draw says "yes" (probability `p`) and the height is below the cap, add one. With `p = 1/4` (Pugh's recommendation, and BusTub's) a level has a quarter of the nodes of the one below, giving about `1/(1-p) = 1.33` links per node and `log_{1/p} n` levels. No rebalancing: the shape is random but its *expected* cost is logarithmic, with no adversarial input that can hurt it unless the generator is predictable.

With a **fixed seed** (BusTub: 15445) the sequence of heights is the same on every run, so a test can say "insert these keys and the nodes must have exactly these heights". Since the sequence has to be the same on every machine and in the C++ course, the course ships a port of `std::mt19937` (the Mersenne Twister) instead of Rust's unspecified generators.

## Memory: pointers or indexes

C++ links nodes with `shared_ptr`; the destructor must free long chains iteratively to avoid a stack overflow. In Rust the nodes live in a `Vec` and a link is the index of a node (an *arena*): no ownership puzzles, no recursion on drop, and the whole structure is freed in one go.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::vector<std::shared_ptr<SkipNode>> links_` | `Vec<Option<usize>>` (indexes into the arena) |
| `std::shared_mutex rwlock_` with `shared_lock` / `unique_lock` | `RwLock<Inner>` with `.read()` / `.write()`; the guard unlocks at scope end |
| `std::mt19937 rng_{Seed}` | a given `Mt19937::new(SEED)` with `next_u32()` |
| `template <typename K, typename Compare, size_t MaxHeight, uint32_t Seed>` | `SkipList<K, const MAX_HEIGHT: usize, const SEED: u32>` plus a boxed comparison closure |

**Port rule:** linked structures in safe Rust are arenas with index links; "next pointer" becomes `Option<usize>`.

## In real code

### Using it: a skip list on indexes

```rust test
const MAX: usize = 8;

struct Node {
    key: i32,
    next: Vec<Option<usize>>, // one link per level
}

struct List {
    nodes: Vec<Node>, // node 0 is the head
    height: usize,
    seed: u32,
}

impl List {
    fn new() -> List {
        List { nodes: vec![Node { key: i32::MIN, next: vec![None; MAX] }], height: 1, seed: 1 }
    }
    fn random_height(&mut self) -> usize {
        let mut h = 1;
        // a tiny linear congruential generator: 1 chance in 4 to grow
        while h < MAX {
            self.seed = self.seed.wrapping_mul(1664525).wrapping_add(1013904223);
            if (self.seed >> 16) % 4 != 0 {
                break;
            }
            h += 1;
        }
        h
    }
    fn search(&self, key: i32) -> (Vec<usize>, Option<usize>) {
        let mut update = vec![0; MAX];
        let mut cur = 0;
        for level in (0..self.height).rev() {
            while let Some(n) = self.nodes[cur].next[level] {
                if self.nodes[n].key < key {
                    cur = n;
                } else {
                    break;
                }
            }
            update[level] = cur;
        }
        let found = self.nodes[cur].next[0].filter(|&n| self.nodes[n].key == key);
        (update, found)
    }
    fn insert(&mut self, key: i32) -> bool {
        let (update, found) = self.search(key);
        if found.is_some() {
            return false;
        }
        let h = self.random_height();
        let old_height = self.height;
        self.height = self.height.max(h);
        let id = self.nodes.len();
        self.nodes.push(Node { key, next: vec![None; h] });
        for level in 0..h {
            let prev = if level < old_height { update[level] } else { 0 };
            self.nodes[id].next[level] = self.nodes[prev].next[level];
            self.nodes[prev].next[level] = Some(id);
        }
        true
    }
    fn contains(&self, key: i32) -> bool {
        self.search(key).1.is_some()
    }
}

#[test]
fn search_finds_what_was_inserted_and_only_that() {
    let mut l = List::new();
    for k in [5, 1, 9, 3, 7] {
        assert!(l.insert(k));
    }
    assert!(!l.insert(5));
    assert!((1..=9).step_by(2).all(|k| l.contains(k)));
    assert!(!l.contains(4) && !l.contains(100));
}

#[test]
fn level_zero_is_sorted_and_higher_levels_are_subsets() {
    let mut l = List::new();
    for k in (0..200).rev() {
        l.insert(k * 3 % 101);
    }
    let level = |lv: usize| {
        let mut out = vec![];
        let mut cur = l.nodes[0].next[lv];
        while let Some(n) = cur {
            out.push(l.nodes[n].key);
            cur = l.nodes[n].next.get(lv).copied().flatten();
        }
        out
    };
    let (l0, l1) = (level(0), level(1));
    assert!(l0.windows(2).all(|w| w[0] < w[1]));
    assert!(l1.iter().all(|k| l0.contains(k)));
    assert!(l1.len() < l0.len());
}
```

### Using it: the geometric height distribution

```rust test
#[test]
fn a_one_in_four_coin_gives_one_and_a_third_links_per_node_on_average() {
    let mut x = 12345u32;
    let mut total = 0usize;
    let n = 100_000;
    for _ in 0..n {
        let mut h = 1;
        while h < 14 {
            x = x.wrapping_mul(1664525).wrapping_add(1013904223);
            if (x >> 16) % 4 != 0 {
                break;
            }
            h += 1;
        }
        total += h;
    }
    let avg = total as f64 / n as f64;
    assert!((1.25..1.42).contains(&avg), "average height {avg}");
}

#[test]
fn the_same_seed_gives_the_same_heights() {
    let draw = |seed: u32| {
        let mut x = seed;
        (0..20).map(|_| { x = x.wrapping_mul(1664525).wrapping_add(1013904223); x >> 16 }).collect::<Vec<_>>()
    };
    assert_eq!(draw(15445), draw(15445));
    assert_ne!(draw(15445), draw(15446));
}
```

### In the exercises

- **0b-01:** the search with its update vector, and insert / contains.
- **0b-02:** erase and clear.
- **0b-03:** BusTub's concurrency tests: readers share the lock, writers exclude everyone.

### Where it is used

- **Redis** sorted sets (`ZSET`) use a skip list beside a hash table.
- **LevelDB / RocksDB** memtables are skip lists (concurrent, lock-free reads).
- **Java's `ConcurrentSkipListMap`**, **Lucene** postings, and Pugh's original 1990 paper "Skip Lists: A Probabilistic Alternative to Balanced Trees".
