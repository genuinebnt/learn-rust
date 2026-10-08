**Where this fits.** Now the first replacer. A **replacer** tracks which buffer-pool frames may be evicted and chooses the victim. **LRU** evicts the frame that was *unpinned* longest ago.

## The task

`Replacer` (given, `src/buffer/replacer.rs`) is the trait: `victim`, `pin`, `unpin`, `size`. `LruReplacer` (`src/buffer/lru_replacer.rs`) keeps an `IndexList<FrameId>` (oldest at the front) and a `HashMap<FrameId, Handle>` that says where each frame is. Implement:
- `unpin(frame)`: add the frame at the back of the list and remember its handle. A frame that is **already** there stays where it is (BusTub's rule). If the list already holds `capacity` frames, panic with a message containing "full";
- `size()`: how many frames the replacer holds.

## Tests

- 6 unpins give size 6; unpinning a frame twice counts it once; a 3rd frame on a 2-frame replacer panics ("full").
- The replacer works as a `Box<dyn Replacer>`.

## Syntax and methods

```rust
if self.handles.contains_key(&frame) { return; }
let handle = self.list.push_back(frame);
self.handles.insert(frame, handle);
assert!(self.list.len() < self.capacity, "the replacer is full: ...");
let mut r: Box<dyn Replacer> = Box::new(LruReplacer::new(3));      // a trait object
```

## Notes

**Pinned vs evictable.** In the buffer pool a frame holding a page that someone is using is *pinned* and must not be evicted. The replacer only holds *unpinned* frames: `unpin` adds, `pin` removes, `victim` picks among what is there. `size()` is therefore "how many frames could I evict right now".

**Where did BusTub's latch go?** C++'s replacers have a `std::mutex latch_` in each method. These take `&mut self` and are meant to live inside the buffer pool's mutex, so the compiler guarantees no two threads use one at the same time.

## In BusTub

```cpp
void LRUReplacer::Unpin(frame_id_t frame_id) {            // (student code in the course; this is the usual shape)
  std::scoped_lock lock(latch_);
  if (pos_.count(frame_id) != 0) { return; }
  lru_list_.push_back(frame_id);  pos_[frame_id] = std::prev(lru_list_.end());
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `virtual auto Victim(frame_id_t *frame_id) -> bool = 0;` (bool + out-parameter) | `fn victim(&mut self) -> Option<FrameId>` |
| `class LRUReplacer : public Replacer` | `impl Replacer for LruReplacer` |
| `std::unordered_map<K, V>`; `map.count(k)`, `map[k] = v` | `HashMap<K, V>`; `contains_key(&k)`, `insert(k, v)` |
| `std::scoped_lock lock(latch_);` in every method | `&mut self` + the owner's mutex |
| `frame_id_t` (an `int32_t`, with `-1` meaning none) | `FrameId(usize)`, and `Option<FrameId>` for "none" |
| assertion/throw on misuse (`BUSTUB_ASSERT`, `throw Exception`) | `assert!` / `panic!` for bugs, `Result` for recoverable errors |

**Port rule:** the "bool return + out-parameter" idiom (`bool Get(K, V *out)`) is always `Option<V>` (or `Result<V, E>`).

## Learn more
- [Page replacement algorithms](https://en.wikipedia.org/wiki/Page_replacement_algorithm) · [Cache replacement policies](https://en.wikipedia.org/wiki/Cache_replacement_policies) · OSTEP, [Beyond physical memory: policies](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- CMU 15-445, "Memory Management" lecture (linked under Module resources)
