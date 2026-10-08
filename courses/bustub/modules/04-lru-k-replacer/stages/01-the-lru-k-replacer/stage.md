This stage has 7 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · LruKNode::record: keep the last k accesses

**Where this fits.** Plain LRU remembers only *when a page was last used*. A page scanned once looks as "recent" as a page used all day. **LRU-K** remembers the last **k** access times of every frame and judges frames by the k-th most recent one: a scan touches each page once, so scanned pages never build a k-deep history and are evicted first.

### The task

`LruKNode` (`src/buffer/lru_k_replacer.rs`) is what the replacer remembers about one frame: a `VecDeque<usize>` of timestamps (oldest first), `k`, the frame id and an evictable flag. The fields are a starting point. Implement `record(timestamp)`: add the access at the **back**; if the history is now longer than `k`, drop the **oldest**.

### Tests

- A new node has no history. After accesses at 10, 11, 12 the oldest kept is 10.
- With k = 3 and accesses 1..=5, the history is 3, 4, 5 (`first_timestamp` is 3); a sixth moves it to 4. With k = 1 only the latest remains.
- 10,000 accesses with k = 4 keep a bounded history (oldest kept 9,996).

### Syntax and methods

```rust
self.history.push_back(timestamp);       // VecDeque: O(1) at both ends
if self.history.len() > self.k { self.history.pop_front(); }
self.history.front().copied()            // Option<&usize> -> Option<usize>
```

### Notes

A `VecDeque` is a ring buffer in a `Vec`: `push_back` and `pop_front` are O(1), unlike `Vec::remove(0)` which shifts everything. It is Rust's `std::deque`/`std::queue`. A bounded history that forgets its oldest entry is a **sliding window** (also the shape of rate limiters and moving averages).

### In BusTub

```cpp
class LRUKNode {
  std::list<size_t> history_;   // "Least recent timestamp stored in front."
  size_t k_;  frame_id_t fid_;  bool is_evictable_{false};
};
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::list<size_t>` (a linked list for a small queue of numbers: cache-hostile) | `VecDeque<usize>` (contiguous ring buffer) |
| `history_.push_back(t); if (history_.size() > k_) history_.pop_front();` | the same two calls |
| `history_.front()` on an empty list: undefined behaviour | `front()` returns `Option<&usize>` |
| `size_t` timestamps | `usize`; or `u64` if it must not depend on pointer width |

**Port rule:** `std::list` of small values is almost always a `VecDeque` (or a `Vec`) in Rust; keep a linked list only when you need O(1) removal from the middle by handle (stage 1c-01).

### Learn more
- [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · C++ [`std::deque`](https://en.cppreference.com/w/cpp/container/deque)
- The paper: O'Neil, O'Neil, Weikum, [The LRU-K page replacement algorithm for database disk buffering](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p297-o_neil.pdf) (SIGMOD 1993)

## Part 2 · LruKNode::kth_timestamp: backward k-distance

**Where this fits.** The number the policy ranks frames by.

### The task

Implement `kth_timestamp()` in `src/buffer/lru_k_replacer.rs`: the timestamp of the **k-th most recent access** (the oldest one kept), or `None` if there have been fewer than `k` accesses. `None` means the **backward k-distance is +infinity** ("never accessed k times"). The distance itself is `now − kth_timestamp`; you never need `now`, since the oldest k-th timestamp is the largest distance.

### Tests

- With k = 3: `None` after 0, 1 and 2 accesses; `Some(oldest)` once there are 3, and it moves forward as old accesses fall out.
- With k = 1 it is the latest access.

### Syntax and methods

```rust
if self.history.len() < self.k { None } else { self.history.front().copied() }
```

### Notes

`Option<usize>` here carries a real idea: **infinity**. Modelling "no value yet, and it ranks above every value" as `None` is natural; ordering it is the next stages' job. (`Option<T>` orders `None < Some(_)`, which is the *opposite* of what we want for distance, a trap in stage 6.)

### In BusTub

"A frame with less than k historical references is given +inf as its backward k-distance. When multiple frames have +inf backward k-distance, classical LRU is used to choose victim." (the header comment of `lru_k_replacer.h`)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::numeric_limits<size_t>::max()` or `INFINITY` as a sentinel for "infinite" | `None` |
| `-1` / `SIZE_MAX` as "not found" in an unsigned type | `Option<usize>` |
| comparing a sentinel by accident with a real value | the type forces you to handle `None` |

**Port rule:** in-band sentinels (`-1`, `UINT_MAX`, `nullptr`, `end()`) become `Option`. Decide explicitly how `None` ranks when you sort.

### Learn more
- [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) · The Rust Book: [the `Option` enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values)

## Part 3 · LruKReplacer: new, record_access, size

**Where this fits.** The replacer owns the nodes, a clock and the counts.

### The task

In `src/buffer/lru_k_replacer.rs`, `LruKReplacer`:
- `new(num_frames, k)`: empty maps and counters; **panic** with a message containing "at least 1" if `k` is 0;
- `record_access(frame)`: **panic** with a message containing "out of range" if `frame >= num_frames`; create the frame's node if it is new (**not evictable**); record the access at the current time (`current_timestamp`), then advance the clock by one;
- `size()`: how many frames are evictable (still 0: no way to make one evictable yet).

### Tests

- A new replacer has size 0; recording frames leaves size 0 (they start non-evictable); every frame `0..num_frames` is accepted.
- Frame `num_frames`, or 1000, panics ("out of range"); `k = 0` panics ("at least 1").

### Syntax and methods

```rust
let node = self.node_store.entry(frame).or_insert_with(|| LruKNode::new(frame, k));   // HashMap::entry: find or create in one lookup
node.record(now);
assert!(frame.0 < self.replacer_size, "frame {} is out of range for a replacer of {} frames", frame.0, self.replacer_size);
```

### Notes

The clock is a plain counter: only the *order* of accesses matters, not real time, which makes the policy deterministic and testable (a wall clock would make ties and tests flaky). `entry().or_insert_with(..)` is the idiomatic replacement for C++'s `if (map.find(k) == map.end()) map[k] = ...; map[k].use()`: one lookup, no double hashing, no default-construct-then-assign.

### In BusTub

```cpp
void LRUKReplacer::RecordAccess(frame_id_t frame_id, AccessType access_type) {
  // Throw an exception if frame_id is invalid (larger than replacer_size_).
  // Update the access history; create the node if the frame is new. A new frame is NOT evictable by default.
}
```

(BusTub's version also takes an `AccessType` (lookup/scan/index) so a leaderboard solution can treat scans specially; the port leaves it out.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `node_store_[frame_id]` inserts a default node if missing (`operator[]`) | `entry(frame).or_insert_with(..)`: explicit |
| `throw std::invalid_argument(..)` for a bad frame id | `assert!` / `panic!` for a programming error, `Result` for a recoverable one |
| `std::mutex latch_` in every method | `&mut self`; the owner locks |
| `size_t current_timestamp_{0}; ++current_timestamp_;` | `self.current_timestamp += 1;` |
| `std::unordered_map<frame_id_t, LRUKNode>` | `HashMap<FrameId, LruKNode>` |

### Learn more
- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry) · [`Entry::or_insert_with`](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html#method.or_insert_with) · The Rust Book: [hash maps](https://doc.rust-lang.org/book/ch08-03-hash-maps.html)

## Part 4 · set_evictable: which frames may go

**Where this fits.** A frame in use (pinned) must not be evicted. The buffer pool tells the replacer with `set_evictable(frame, false/true)`.

### The task

Implement `set_evictable(frame, evictable)` in `src/buffer/lru_k_replacer.rs`: change the frame's flag and keep `curr_size` (the number of evictable frames) correct. A frame the replacer has never seen is ignored. Setting a flag to the value it already has changes nothing (and must not skew the count).

### Tests

- Of frames 1..6 with 1..5 set evictable and 6 not, `size()` is 5.
- Setting `true` twice counts once; toggling goes up and down; an unknown frame is ignored; further accesses keep the flag.

### Syntax and methods

```rust
let Some(node) = self.node_store.get_mut(&frame) else { return };   // get_mut: Option<&mut V>
if node.is_evictable != evictable { /* update flag and count together */ }
```

### Notes

`curr_size` is **derived state**: it could be computed by counting nodes. Keeping a counter is faster (`size()` is called often) but means *every* place that changes a flag, or removes a node, must update it. The two classic bugs: counting a no-op change, and forgetting it in `evict`/`remove`. When you feel the urge to cache a count, write the test that checks the cache against a recount (stage 6's model test does).

### In BusTub

"Set the evictable status of a frame. Note that replacer's size is the number of evictable frames. If a frame was previously evictable and is to be set to non-evictable, then size should decrement. If a frame was previously non-evictable and is to be set to evictable, then size should increment." (`SetEvictable` comment)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = node_store_.find(id); if (it == node_store_.end()) return; it->second.is_evictable_ = ...` | `let Some(node) = self.node_store.get_mut(&id) else { return };` |
| `size_t curr_size_` decremented below zero: wraps to 18446744073709551615 | `usize` underflow panics in debug builds (use the invariant, not `wrapping_sub`) |
| `bool` flags mutated through public members | private fields + methods |

### Learn more
- [`HashMap::get_mut`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.get_mut) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Part 5 · evict: the least recently used among the infinite

**Where this fits.** The point of the whole module: choosing a victim.

### The task

In `src/buffer/lru_k_replacer.rs`, implement `evict()` and the pieces it needs (`pick_victim` and `remove_node` are the suggested helpers):
- among the **evictable** frames, choose the victim: for now, treat every frame as if it had fewer than `k` accesses, so the victim is the frame whose **first** (oldest kept) access is oldest: LRU;
- remove its node (history gone, `curr_size` down by one) and return it;
- `None` if no frame is evictable (and change nothing).

### Tests

- One access each: victims in order of access. Frames not made evictable are skipped, and `evict` on them gives `None`.
- `evict` lowers `size`; a failed `evict` does not.
- **An evicted frame starts over:** when it is recorded again it is a new frame, not evictable until marked.
- With `k = 3`, frames with 1 and 2 accesses are both "infinite": the older **first** access goes first, not the older latest one.

### Syntax and methods

```rust
self.node_store.values().filter(|n| n.is_evictable()).min_by_key(|n| n.first_timestamp()).map(|n| n.frame_id())
let victim = self.pick_victim()?;                         // `?` on Option: return None if there is no victim
self.node_store.remove(&victim)                           // HashMap::remove -> Option<V>
```

### Notes

`Iterator::min_by_key` scans everything: this is O(n) per eviction, which is fine for the tests and wrong for a pool of a million frames (stage 8 fixes that). Write the obviously-correct version first; the test suite then protects the fast one.

### In BusTub

"Find the frame with largest backward k-distance and evict that frame. Only frames that are marked as 'evictable' are candidates for eviction. ... Successful eviction of a frame should decrement the size of replacer and remove the frame's access history."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min_element(first, last, comp)` returns an iterator; `end()` when empty (dereferencing it is UB) | `min_by_key(..)` returns `Option` |
| a hand-written loop with a "best so far" variable and a `bool found` | `filter` + `min_by_key` + `map` |
| `std::optional<frame_id_t> Evict()` | `Option<FrameId>` |
| `node_store_.erase(it)` | `node_store.remove(&k)` |

### Learn more
- [`Iterator::min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key) · [`Iterator::filter`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter) · C++ [`std::min_element`](https://en.cppreference.com/w/cpp/algorithm/min_element)

## Part 6 · evict: infinite distances first, then the oldest k-th access

**Where this fits.** Frames that have been accessed `k` times now compete properly.

### The task

Change the victim choice in `src/buffer/lru_k_replacer.rs` to the real rule: a frame with fewer than `k` accesses (distance +infinity) beats any frame with `k` accesses; among the infinite ones the **oldest first access** goes first; among the finite ones the **oldest k-th most recent access** goes first (that is the largest backward k-distance).

### Tests

- A one-access frame is evicted before a two-access frame (k = 2).
- Two full histories: the older k-th access goes first, even if the other frame was touched more recently overall. Frame 1 touched most recently overall but with an old 2nd-latest access is still evicted before frame 2 (plain LRU would keep frame 1).
- The walkthrough from BusTub's sample test, step by step.
- A **model test**: 30 seeded random workloads (varying k = 1..3) agree, evict by evict, with a slow reference that recomputes everything from the full access log.

### Syntax and methods

```rust
.min_by_key(|n| match n.kth_timestamp() {
    None => (0, n.first_timestamp()),        // infinite: group 0, ordered by first access
    Some(t) => (1, Some(t)),                 // finite: group 1, ordered by the k-th access
})
```

### Notes

A tuple key sorts lexicographically, so `(0, ..)` comes before `(1, ..)`: **encode a multi-level priority as a tuple**. The trap this avoids is `Option`'s own ordering: `None < Some(_)`, which would put the infinite frames first by accident *here*, and the wrong way round if you ever compare distances rather than timestamps. Make the intent explicit.

The two other ties: two frames can't have the same timestamp (the clock advances on every access), so no further tie-break is needed. (Stage 8's ordered set adds the frame id to its key anyway, so equal keys can coexist.)

### In BusTub

"Backward k-distance is computed as the difference in time between current timestamp and the timestamp of kth previous access. A frame with less than k historical references is given +inf as its backward k-distance. When multiple frames have +inf backward k-distance, the replacer evicts the frame with the earliest timestamp overall."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a comparator `[](auto &a, auto &b) { if (a.inf != b.inf) return a.inf; ... }` passed to `std::min_element` | a key function returning a tuple (or implement `Ord`) |
| `std::pair`/`std::tuple` compare lexicographically with `operator<` | tuples are `Ord` lexicographically |
| `std::numeric_limits<size_t>::max()` as the "infinite" distance | `None`, or a group number as here |
| sorting floating-point keys needs care with NaN | `f64` isn't `Ord`; use integers or `total_cmp` |

### Learn more
- [`Ord` and lexicographic tuple ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html) · [`min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key)
- The LRU-K [paper](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p297-o_neil.pdf), section 2 (the definition) and the "correlated reference period" idea BusTub leaves out

## Part 7 · remove: take a frame out of the replacer

**Where this fits.** When the buffer pool deletes a page, its frame leaves the replacer without being "evicted".

### The task

Implement `remove(frame)` in `src/buffer/lru_k_replacer.rs`: drop an **evictable** frame and its history, whatever its distance. A frame the replacer doesn't hold is ignored. Removing a frame that is **not evictable** is a bug in the caller: panic with a message containing "not evictable".

### Tests

- Remove frame 2 of 1, 2, 3: size 2, victims 1 then 3. Unknown frames: nothing happens. Non-evictable: panics.
- A removed frame has no history left: record it again and it is a brand-new frame. Removing every frame leaves an empty replacer.

### Syntax and methods

```rust
let Some(node) = self.node_store.get(&frame) else { return };
assert!(node.is_evictable(), "frame {} is not evictable and cannot be removed", frame.0);
```

### Notes

`remove` is `evict`'s sibling: the same bookkeeping (drop the node, lower the count) for a frame *chosen by the caller* instead of by the policy. Share the code (`remove_node`), so the count has one place to go wrong.

### In BusTub

"Remove an evictable frame from replacer, along with its access history. This function should also decrement replacer's size if removal is successful. Note that this is different from evicting a frame, which always remove the frame with largest backward k-distance. ... If Remove is called on a non-evictable frame, throw an exception. If specified frame is not found, directly return from this function."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::logic_error(..)` | `assert!(..)` / `panic!` (a bug), or return `Result` if callers can recover |
| "if not found, directly return" | `let Some(..) = .. else { return }` |
| exceptions propagate through the buffer pool and may unwind past locks | a panic poisons the mutex that was held, and the owner decides what to do |

### Learn more
- The Rust Book: [to panic! or not to panic!](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)
