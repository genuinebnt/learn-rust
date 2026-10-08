This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

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

- Unpin 3, 1, 2: victims come out 3, 1, 2, then `None`. A victim leaves the replacer (`size` shrinks).
- Unpinning a frame that is already there does **not** refresh it: unpin 1, 2, 1, and 1 is still the first victim.
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

- A pinned frame is never a victim; pinning an unknown frame, or the same frame twice, changes nothing.
- Unpinning after a pin puts the frame at the back.
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
