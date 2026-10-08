This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

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
