A skip list is a sorted linked list with express lanes: every node has a random height and takes part in that many levels. This stage writes the core: the **search** (from the top level, go right while the next key is before the sought one, then drop a level), which also returns the **update vector** (the last node visited on every level), and **insert** and **contains** built on it.

## The task

In `src/primer/skiplist.rs`:

- `SkipNode::new(height, key)`, `height()`, `next(level)`, `set_next(level, next)`: the node's accessors (a `Vec` of links; a link is the index of another node in the arena, or `None`).
- `Inner::search(compare, key) -> (update, found)`: walk from `height - 1` down to 0; on each level move while the next node's key is before `key` (`compare(next_key, key)`); record the node you stop at in `update[level]`. The candidate is the next node on level 0; it is `found` if `key` is not before the candidate's key (equivalence, as in `std::set`).
- `SkipList::insert(&key)`: write lock; search; an equivalent key: `false`; draw a height (`random_height`, given); if it exceeds the list's height raise it (levels above the old height start at the header); allocate the node (`alloc`, given); on each level `0..height` link it between `update[level]` and that node's next; size + 1.
- `contains`: read lock, search. `size`: read lock.

## Tests

- A new list is empty; insert and contains; duplicates are refused and change nothing.
- The list stays sorted for any insertion order; a comparison function decides the order.
- Node heights are exactly BusTub's, for the fixed seed.
- Strings work too.

## Syntax and methods

```rust
let (update, found) = inner.search(&self.compare, key);
let id = inner.alloc(SkipNode::new(new_height, Some(key.clone())));
let prev = if level < old_height { update[level] } else { HEADER };
let next = inner.nodes[prev].next(level);
inner.nodes[id].set_next(level, next);
inner.nodes[prev].set_next(level, Some(id));
```

## Notes

**The comparison is "is before".** Like `std::less`, `compare(a, b)` means a precedes b. Two keys are *equivalent* when neither precedes the other; that is the duplicate test, and why a list ordered by `>` works unchanged.

**Why the update vector.** After the search you know, for every level, which node must point to the new one. Without it you would search again for each level.

**New levels.** A node taller than the list has no predecessor recorded above the old height: the header is the predecessor there, and its links on those levels are empty.

**Heights are reproducible.** `random_height` draws from a port of `std::mt19937` seeded with the list's `SEED` (15445). The test in this stage lists the heights BusTub's test expects for 20 keys; if your search or insert draws a random number it should not (for a duplicate, say), the sequence shifts and the heights no longer match.

## In BusTub

`skiplist.h`: "`The skip list is implemented as a linked list of nodes. Each node has a list of forward links. The number of forward links is determined by a geometric distribution. The skip list maintains a header node that is always at the maximum height of the skip list.`" and `RandomHeight`: "`Branching factor (1 in 4 chance), see Pugh's paper.`". The test `IntegrityCheckTest` checks the shape.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<SkipNode>` links, `links_[level]` | `Option<usize>` links into `nodes: Vec<SkipNode>` |
| `Compare compare_` template parameter | a boxed closure `Fn(&K, &K) -> bool` |
| `std::shared_lock` / `std::unique_lock` on `rwlock_` | `inner.read().unwrap()` / `inner.write().unwrap()` |

**Port rule:** in safe Rust a node does not own its successor; the list owns all nodes and links name them by index.

## Learn more
- [Pugh's paper](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf) · [`RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html)

## Performance

Expected `O(log n)` per operation: with branching factor 1/4 the list has about `log_4 n` levels and a search takes about `(4/3) × log_4 n` steps per level... in total roughly `1.3 × log_4(n) × 3` comparisons. The worst case is `O(n)` but its probability is negligible.

**Measure it.** Count the comparisons for 1 000, 10 000 and 100 000 keys: each tenfold increase adds a constant, not tenfold.

## Hints

### Draw the height only for a new key

Check for the duplicate first; drawing a height for a rejected insert consumes a random number and changes every later height.

### The comparison for `found` goes the other way

Candidate is found when `!compare(key, candidate_key)`: you already know `candidate_key` is not before `key` (the search stopped there).

### Raise the height before linking

`update` only has entries below the old height; use the header for the new levels.
