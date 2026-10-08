This stage has 6 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

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

## Part 4 · ClockReplacer: the ring, unpin and size

**Where this fits.** LRU needs a list update on every access. **CLOCK** approximates LRU with one bit per frame and a sweeping hand: much cheaper, and what PostgreSQL and the Linux kernel's page cache use.

### The task

`ClockReplacer` (`src/buffer/clock_replacer.rs`) keeps a ring of `(FrameId, bool)` (the bool is the **reference bit**) and a `hand`. Implement:
- `unpin(frame)`: a frame already on the ring gets its reference bit set; a new frame is added at the **end** of the ring with its bit set. If the ring already has `capacity` frames, panic with "full";
- `size()`: how many frames are on the ring.

### Tests

- 6 unpins give size 6; unpinning twice counts once; a 2nd frame on a 1-frame replacer panics ("full").

### Syntax and methods

```rust
match self.ring.iter_mut().find(|(f, _)| *f == frame) {     // iter_mut + find: a mutable reference to the slot, if any
    Some(slot) => slot.1 = true,                              // tuple fields: .0 and .1
    None => self.ring.push((frame, true)),
}
```

### Notes

**Why CLOCK.** On a page hit, LRU must move the page in a shared list: a lock and several writes. CLOCK only sets a bit. The hand does the work later, on eviction: it gives a frame with its bit set "a second chance" by clearing the bit; the first frame whose bit is already clear is the victim. The ring can be a plain `Vec` because the hand moves forward only; searching for a frame is `O(n)` here, which is fine for the sweep and the reason real implementations store the bit inside the frame's own header.

### In BusTub

```cpp
class ClockReplacer : public Replacer { /* TODO(student): implement me! */ };
```

(BusTub gives no implementation and a single sample test; the textbook algorithm is what is expected.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `struct { frame_id_t id; bool ref; }` array + `size_t hand` | `Vec<(FrameId, bool)>` + `usize` |
| `std::find_if(v.begin(), v.end(), [&](auto &e){ return e.id == f; })` | `iter().find(\|(f, _)\| *f == frame)` |
| a reference bit per frame in the buffer descriptor (`BufferDesc.usage_count` in PostgreSQL) | in the frame header, atomically |
| `std::vector<bool>` (a packed bitset with a proxy reference) | `Vec<bool>` is one byte per bool (use `bitvec`/a `u64` for packing) |

### Learn more
- [Clock page replacement](https://en.wikipedia.org/wiki/Page_replacement_algorithm#Clock) · PostgreSQL's [`freelist.c`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/freelist.c) (`StrategyGetBuffer`: the clock sweep) · Linux [`mm/workingset.c`](https://github.com/torvalds/linux/blob/master/mm/workingset.c)

## Part 5 · ClockReplacer::victim: the sweep

**Where this fits.** The hand at work.

### The task

Implement `victim()` in `src/buffer/clock_replacer.rs`: look at the frame under the `hand`. If its reference bit is **set**, clear it and move the hand to the next frame (wrapping to the start); if it is **clear**, remove that frame from the ring and return it, leaving the hand on whatever follows it. An empty ring gives `None`. (A ring whose bits are all set takes one full lap to clear them, then returns the frame the hand started on.)

### Tests

- Frames 1..4 all unpinned: victims 1, 2, 3, 4, then `None`.
- **Second chance:** after victim 1, unpin 2 again: the next victim is **3**, then 4, then 2.
- A new frame joins at the end; a lone frame with its bit set is still evicted; an empty ring is `None`.

### Syntax and methods

```rust
loop {
    if self.ring[self.hand].1 {
        self.ring[self.hand].1 = false;
        self.hand = (self.hand + 1) % self.ring.len();
    } else {
        let (frame, _) = self.ring.remove(self.hand);   // Vec::remove shifts the tail left: the hand now points at the successor
        if self.hand >= self.ring.len() { self.hand = 0; }
        return Some(frame);
    }
}
```

### Notes

The loop terminates because each lap clears every bit it passes. `remove(hand)` is the neat part: after removal the element that *was* next is at `hand`, so the hand needs no adjustment except wrapping past the end. An `% len` on an empty ring would divide by zero, which is why the empty check comes first.

### In BusTub

(No reference code is given; the sample test is the contract: after the sweep, victims `1, 2, 3` and later `5, 6, 4`, where 4 had its reference bit set by a fresh `Unpin`.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `hand = (hand + 1) % ring.size();` (`% 0` is undefined behaviour in C/C++, a panic in Rust) | `% self.ring.len()` after the empty check |
| `ring.erase(ring.begin() + hand)` shifts elements, invalidating iterators at and after the position | `Vec::remove(hand)`: same shift, and the borrow checker prevents holding a reference across it |
| `while (true) { ... }` with `return` inside | `loop { ... return ... }` (a `loop` can only exit by `return`/`break`, and its type is `!` otherwise) |

### Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · [`loop`](https://doc.rust-lang.org/reference/expressions/loop-expr.html#infinite-loops)
- CMU 15-445 "Memory Management", the slides on CLOCK

## Part 6 · ClockReplacer::pin: take a frame off the ring

**Where this fits.** Pinning must not disturb where the hand points.

### The task

Implement `pin(frame)` in `src/buffer/clock_replacer.rs`: remove the frame from the ring if it is there. The `hand` must keep pointing at **the same frame it pointed at before** (if the removed frame was *before* the hand, the hand's index shifts down by one; if it was *at* the hand, the hand now points at its successor), wrapping to 0 when it falls off the end. Unknown frames: nothing happens.

### Tests

- A pinned frame leaves the ring and is never a victim; an unknown frame changes nothing.
- The scenario that breaks a careless version: frames 1..6; victim 1; unpin 2 (second chance); victim 3; **pin 2** (it lies behind the hand): the next victims must be 4, then 5. Pinning the frame under the hand moves on to its successor; pinning the last frame wraps.

### Syntax and methods

```rust
let Some(at) = self.ring.iter().position(|(f, _)| *f == frame) else { return };   // Iterator::position -> Option<usize>
self.ring.remove(at);
if at < self.hand { self.hand -= 1; }
if self.hand >= self.ring.len() { self.hand = 0; }
```

### Notes

This is an **index invalidation** bug waiting to happen, in any language: you store a position, then remove something before it. In C++ the analogue is an iterator or index kept across `erase`. Rust's borrow checker can't help with a plain `usize`; tests do. (If the hand were a reference into the `Vec`, the borrow checker *would* stop you from removing anything while it is held, which is the reason to keep it an index.)

### In BusTub

```cpp
// The sample test: Pin(3) (already victimised, a no-op), Pin(4) (removes it), then Unpin(4) sets the reference bit again.
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = std::find(...); ring.erase(it);` with an index `hand` kept elsewhere: the classic stale-index bug | `position` + `remove` + explicit fix-up of `hand` |
| `std::vector::erase` invalidates iterators/pointers/references at or after the erased element | the same data movement; `&`/`&mut` into the `Vec` can't outlive the call |
| `std::deque`, `std::list` give stable iterators across erases of *other* elements | an arena (stage 1) gives stable handles; a `Vec` ring does not |

**Port rule:** every stored index into a `Vec` is a promise that nothing before it is removed. Either use handles (generational) or fix the index up at every removal, and test it.

### Learn more
- [`Iterator::position`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position) · [`Vec::retain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.retain)
