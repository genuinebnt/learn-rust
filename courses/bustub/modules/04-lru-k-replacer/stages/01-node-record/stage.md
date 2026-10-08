**Where this fits.** Plain LRU remembers only *when a page was last used*. A page scanned once looks as "recent" as a page used all day. **LRU-K** remembers the last **k** access times of every frame and judges frames by the k-th most recent one: a scan touches each page once, so scanned pages never build a k-deep history and are evicted first.

## The task

`LruKNode` (`src/buffer/lru_k_replacer.rs`) is what the replacer remembers about one frame: a `VecDeque<usize>` of timestamps (oldest first), `k`, the frame id and an evictable flag. The fields are a starting point. Implement `record(timestamp)`: add the access at the **back**; if the history is now longer than `k`, drop the **oldest**.

## Tests

- A new node has no history. After accesses at 10, 11, 12 the oldest kept is 10.
- With k = 3 and accesses 1..=5, the history is 3, 4, 5 (`first_timestamp` is 3); a sixth moves it to 4. With k = 1 only the latest remains.
- 10,000 accesses with k = 4 keep a bounded history (oldest kept 9,996).

## Syntax and methods

```rust
self.history.push_back(timestamp);       // VecDeque: O(1) at both ends
if self.history.len() > self.k { self.history.pop_front(); }
self.history.front().copied()            // Option<&usize> -> Option<usize>
```

## Notes

A `VecDeque` is a ring buffer in a `Vec`: `push_back` and `pop_front` are O(1), unlike `Vec::remove(0)` which shifts everything. It is Rust's `std::deque`/`std::queue`. A bounded history that forgets its oldest entry is a **sliding window** (also the shape of rate limiters and moving averages).

## In BusTub

```cpp
class LRUKNode {
  std::list<size_t> history_;   // "Least recent timestamp stored in front."
  size_t k_;  frame_id_t fid_;  bool is_evictable_{false};
};
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::list<size_t>` (a linked list for a small queue of numbers: cache-hostile) | `VecDeque<usize>` (contiguous ring buffer) |
| `history_.push_back(t); if (history_.size() > k_) history_.pop_front();` | the same two calls |
| `history_.front()` on an empty list: undefined behaviour | `front()` returns `Option<&usize>` |
| `size_t` timestamps | `usize`; or `u64` if it must not depend on pointer width |

**Port rule:** `std::list` of small values is almost always a `VecDeque` (or a `Vec`) in Rust; keep a linked list only when you need O(1) removal from the middle by handle (stage 1c-01).

## Learn more
- [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · C++ [`std::deque`](https://en.cppreference.com/w/cpp/container/deque)
- The paper: O'Neil, O'Neil, Weikum, [The LRU-K page replacement algorithm for database disk buffering](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p297-o_neil.pdf) (SIGMOD 1993)
