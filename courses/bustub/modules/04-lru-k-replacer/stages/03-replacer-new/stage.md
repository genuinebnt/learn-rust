**Where this fits.** The replacer owns the nodes, a clock and the counts.

## The task

In `src/buffer/lru_k_replacer.rs`, `LruKReplacer`:
- `new(num_frames, k)`: empty maps and counters; **panic** with a message containing "at least 1" if `k` is 0;
- `record_access(frame)`: **panic** with a message containing "out of range" if `frame >= num_frames`; create the frame's node if it is new (**not evictable**); record the access at the current time (`current_timestamp`), then advance the clock by one;
- `size()`: how many frames are evictable (still 0: no way to make one evictable yet).

## Tests

- A new replacer has size 0; recording frames leaves size 0 (they start non-evictable); every frame `0..num_frames` is accepted.
- Frame `num_frames`, or 1000, panics ("out of range"); `k = 0` panics ("at least 1").

## Syntax and methods

```rust
let node = self.node_store.entry(frame).or_insert_with(|| LruKNode::new(frame, k));   // HashMap::entry: find or create in one lookup
node.record(now);
assert!(frame.0 < self.replacer_size, "frame {} is out of range for a replacer of {} frames", frame.0, self.replacer_size);
```

## Notes

The clock is a plain counter: only the *order* of accesses matters, not real time, which makes the policy deterministic and testable (a wall clock would make ties and tests flaky). `entry().or_insert_with(..)` is the idiomatic replacement for C++'s `if (map.find(k) == map.end()) map[k] = ...; map[k].use()`: one lookup, no double hashing, no default-construct-then-assign.

## In BusTub

```cpp
void LRUKReplacer::RecordAccess(frame_id_t frame_id, AccessType access_type) {
  // Throw an exception if frame_id is invalid (larger than replacer_size_).
  // Update the access history; create the node if the frame is new. A new frame is NOT evictable by default.
}
```

(BusTub's version also takes an `AccessType` (lookup/scan/index) so a leaderboard solution can treat scans specially; the port leaves it out.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `node_store_[frame_id]` inserts a default node if missing (`operator[]`) | `entry(frame).or_insert_with(..)`: explicit |
| `throw std::invalid_argument(..)` for a bad frame id | `assert!` / `panic!` for a programming error, `Result` for a recoverable one |
| `std::mutex latch_` in every method | `&mut self`; the owner locks |
| `size_t current_timestamp_{0}; ++current_timestamp_;` | `self.current_timestamp += 1;` |
| `std::unordered_map<frame_id_t, LRUKNode>` | `HashMap<FrameId, LruKNode>` |

## Learn more
- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry) · [`Entry::or_insert_with`](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html#method.or_insert_with) · The Rust Book: [hash maps](https://doc.rust-lang.org/book/ch08-03-hash-maps.html)
