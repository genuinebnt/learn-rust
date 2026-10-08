The LRU replacer is the baseline policy: it evicts the frame that was **unpinned longest ago**. With the arena list from the previous stage it is almost nothing, which is the point: the structure did the hard part. What remains is the *protocol*: which calls change the order, what `size` counts, and what happens when the same frame is unpinned twice.

The exercise also asks for speed: a replacer built on a scan works and fails the 100 000-frame test.

## Part 1 · LruReplacer: unpin and size

**Where this fits.** Now the first replacer. A **replacer** tracks which buffer-pool frames may be evicted and chooses the victim. **LRU** evicts the frame that was *unpinned* longest ago.

### The task

`Replacer` (given, `src/buffer/replacer.rs`) is the trait: `victim`, `pin`, `unpin`, `size`. `LruReplacer` (`src/buffer/lru_replacer.rs`) keeps an `IndexList<FrameId>` (oldest at the front) and a `HashMap<FrameId, Handle>` that says where each frame is. Implement:
- `unpin(frame)`: add the frame at the back of the list and remember its handle. A frame that is **already** there stays where it is (BusTub's rule). If the list already holds `capacity` frames, panic with a message containing "full";
- `size()`: how many frames the replacer holds.

### Tests

- 6 unpins give size 6; unpinning a frame twice counts it once; a 3rd frame on a 2-frame replacer panics ("full").
- The replacer works as a `Box<dyn Replacer>`.

### Syntax and methods

```rust
if self.handles.contains_key(&frame) { return; }
let handle = self.list.push_back(frame);
self.handles.insert(frame, handle);
assert!(self.list.len() < self.capacity, "the replacer is full: ...");
let mut r: Box<dyn Replacer> = Box::new(LruReplacer::new(3));      // a trait object
```

### Notes

**Pinned vs evictable.** In the buffer pool a frame holding a page that someone is using is *pinned* and must not be evicted. The replacer only holds *unpinned* frames: `unpin` adds, `pin` removes, `victim` picks among what is there. `size()` is therefore "how many frames could I evict right now".

**Where did BusTub's latch go?** C++'s replacers have a `std::mutex latch_` in each method. These take `&mut self` and are meant to live inside the buffer pool's mutex, so the compiler guarantees no two threads use one at the same time.

### In BusTub

```cpp
void LRUReplacer::Unpin(frame_id_t frame_id) {            // (student code in the course; this is the usual shape)
  std::scoped_lock lock(latch_);
  if (pos_.count(frame_id) != 0) { return; }
  lru_list_.push_back(frame_id);  pos_[frame_id] = std::prev(lru_list_.end());
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `virtual auto Victim(frame_id_t *frame_id) -> bool = 0;` (bool + out-parameter) | `fn victim(&mut self) -> Option<FrameId>` |
| `class LRUReplacer : public Replacer` | `impl Replacer for LruReplacer` |
| `std::unordered_map<K, V>`; `map.count(k)`, `map[k] = v` | `HashMap<K, V>`; `contains_key(&k)`, `insert(k, v)` |
| `std::scoped_lock lock(latch_);` in every method | `&mut self` + the owner's mutex |
| `frame_id_t` (an `int32_t`, with `-1` meaning none) | `FrameId(usize)`, and `Option<FrameId>` for "none" |
| assertion/throw on misuse (`BUSTUB_ASSERT`, `throw Exception`) | `assert!` / `panic!` for bugs, `Result` for recoverable errors |

**Port rule:** the "bool return + out-parameter" idiom (`bool Get(K, V *out)`) is always `Option<V>` (or `Result<V, E>`).

### Learn more
- [Page replacement algorithms](https://en.wikipedia.org/wiki/Page_replacement_algorithm) · [Cache replacement policies](https://en.wikipedia.org/wiki/Cache_replacement_policies) · OSTEP, [Beyond physical memory: policies](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- CMU 15-445, "Memory Management" lecture (linked under Module resources)

## Part 2 · LruReplacer::victim

**Where this fits.** When the pool is full and a new page is needed, the replacer names the frame to throw out.

### The task

Implement `victim()` in `src/buffer/lru_replacer.rs`: remove and return the frame at the **front** of the list (the one unpinned longest ago), forgetting its handle; `None` if the replacer is empty.

### Tests

- Unpin 3, 1, 2: victims come out 3, 1, 2, then `None`. A victim leaves the replacer (`size` shrinks). Unpinning a frame that is already there does **not** refresh it: unpin 1, 2, 1, and 1 is still the first victim.
- A victim can be unpinned again and then goes to the back.

### Syntax and methods

```rust
let frame = self.list.pop_front()?;      // `?`: return None if the list is empty
self.handles.remove(&frame);
Some(frame)
```

### Notes

The map and the list must be kept in step: every frame in one is in the other. Whenever you add a second place that remembers something, ask which operations have to update both. (A pattern that comes back in the buffer pool: the page table and the replacer.)

### In BusTub

```cpp
auto LRUReplacer::Victim(frame_id_t *frame_id) -> bool {
  if (lru_list_.empty()) { return false; }
  *frame_id = lru_list_.front();  lru_list_.pop_front();  pos_.erase(*frame_id);  return true;
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `*frame_id = lru_list_.front(); ... return true;` | `Some(frame)` |
| `if (lru_list_.empty()) return false;` guard before `front()` (UB otherwise) | `pop_front()?` |
| two containers to keep in step by discipline | the same, but the types make you write each update |

### Learn more
- LRU in practice: PostgreSQL uses a clock sweep instead ([`freelist.c`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/freelist.c)) because exact LRU needs a lock on every access · [crate `lru`](https://docs.rs/lru) is the ready-made cache

## Part 3 · LruReplacer::pin, and speed

**Where this fits.** A frame in use must not be evicted: pinning takes it out of the replacer.

### The task

Implement `pin(frame)` in `src/buffer/lru_replacer.rs`: if the replacer holds the frame, remove it from the list and the map; otherwise do nothing. Everything must be **O(1)**.

### Tests

- A pinned frame is never a victim; pinning an unknown frame, or the same frame twice, changes nothing. Unpinning after a pin puts the frame at the back.
- **Speed:** 200,000 unpins, 100,000 pins, 50,000 more unpins and a drain of all victims finish in under 5 seconds (a `Vec`-and-`position` solution takes minutes).

### Syntax and methods

```rust
if let Some(handle) = self.handles.remove(&frame) {   // HashMap::remove returns the removed value
    self.list.remove(handle);
}
```

### Notes

The speed test is the reason for the index list: with a `VecDeque`, `pin` must search for the frame (`O(n)`), and a buffer pool of a million frames pins and unpins on every page access. "Fine for the tests" and "fine for 200,000 frames" are different requirements.

### In BusTub

```cpp
void LRUReplacer::Pin(frame_id_t frame_id) {
  auto it = pos_.find(frame_id);
  if (it == pos_.end()) { return; }
  lru_list_.erase(it->second);  pos_.erase(it);
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = m.find(k); if (it == m.end()) return; ... m.erase(it);` | `if let Some(h) = m.remove(&k) { ... }` (lookup and erase in one) |
| `std::find(v.begin(), v.end(), x)` on a vector: O(n) | `HashMap` for position, arena for order |
| complexity is a comment ("O(1) amortised") | complexity is a test (`Instant::now()` + an assertion) |

### Learn more
- [`HashMap::remove`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.remove) · Postgres' buffer manager README: [`storage/buffer/README`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/README) (pins, usage counts, the clock sweep)

## Performance

With the handle map every operation is O(1): `unpin` is a hash lookup and a `push_back` or `move_to_back`; `pin` is a hash lookup and a `remove`; `victim` is a `pop_front` and a hash removal. The scan-based alternative (a `Vec` of frames searched for each call) is O(n) per operation, so 100 000 operations over 100 000 frames is about 10<sup>10</sup> steps: tens of seconds, against milliseconds for the handle version.

An LRU **hit costs a list write**, and in a concurrent buffer pool that write needs the pool's lock on every access: that is the cost the CLOCK replacer exists to avoid (next stage).

**Measure it.** Time 1 000 000 `unpin`/`pin`/`victim` operations at 1 000, 10 000 and 100 000 frames: the time per operation should not grow with the frame count. Replay the reference string `1 2 3 4 1 2 5 1 2 3 4 5` through a model of FIFO and your LRU and check you get 9/10 and 10/8 faults with 3 and 4 frames.

## Hints

### What does `unpin` do for a frame that is already in the list?

Calling `unpin` on a frame that is already evictable must not add a second copy. This replacer **ignores** the repeat: the frame keeps the place it earned when it was first unpinned, because "evict the one unpinned longest ago" is about the *last transition from pinned to unpinned*, and nothing was pinned in between. (Moving it to the back would make a harmless duplicate call change the eviction order.) The list and the map must agree afterwards: one entry in each, and `size()` equal to the number of frames in the list. Also decide what happens when the replacer is already full; BusTub treats it as a bug in the caller.

### The map and the list are two views of one fact

Every evictable frame is in the list *and* in the map (frame to handle); a frame is in neither otherwise. Operations that change one must change the other in the same call, and `victim` must remove the popped frame from the map too: forgetting that leaves a map entry whose handle is stale, so a later `pin` of that frame calls `remove` on a dead handle and the size drifts. A `check()` that compares `list.len()`, `map.len()` and `size()` after every operation finds this in the first test that evicts.

### Speed is part of the specification

The speed test makes an O(n) `victim` or `pin` fail by timing out rather than by a wrong answer. If you reach for `Vec::position` or `retain`, the arena handle is what replaces it: `pin(frame)` should look up the handle and `remove` it, never walk the list.
