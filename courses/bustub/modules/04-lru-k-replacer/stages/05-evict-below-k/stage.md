**Where this fits.** The point of the whole module: choosing a victim.

## The task

In `src/buffer/lru_k_replacer.rs`, implement `evict()` and the pieces it needs (`pick_victim` and `remove_node` are the suggested helpers):
- among the **evictable** frames, choose the victim: for now, treat every frame as if it had fewer than `k` accesses, so the victim is the frame whose **first** (oldest kept) access is oldest: LRU;
- remove its node (history gone, `curr_size` down by one) and return it;
- `None` if no frame is evictable (and change nothing).

## Tests

- One access each: victims in order of access. Frames not made evictable are skipped, and `evict` on them gives `None`.
- `evict` lowers `size`; a failed `evict` does not.
- **An evicted frame starts over:** when it is recorded again it is a new frame, not evictable until marked.
- With `k = 3`, frames with 1 and 2 accesses are both "infinite": the older **first** access goes first, not the older latest one.

## Syntax and methods

```rust
self.node_store.values().filter(|n| n.is_evictable()).min_by_key(|n| n.first_timestamp()).map(|n| n.frame_id())
let victim = self.pick_victim()?;                         // `?` on Option: return None if there is no victim
self.node_store.remove(&victim)                           // HashMap::remove -> Option<V>
```

## Notes

`Iterator::min_by_key` scans everything: this is O(n) per eviction, which is fine for the tests and wrong for a pool of a million frames (stage 8 fixes that). Write the obviously-correct version first; the test suite then protects the fast one.

## In BusTub

"Find the frame with largest backward k-distance and evict that frame. Only frames that are marked as 'evictable' are candidates for eviction. ... Successful eviction of a frame should decrement the size of replacer and remove the frame's access history."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min_element(first, last, comp)` returns an iterator; `end()` when empty (dereferencing it is UB) | `min_by_key(..)` returns `Option` |
| a hand-written loop with a "best so far" variable and a `bool found` | `filter` + `min_by_key` + `map` |
| `std::optional<frame_id_t> Evict()` | `Option<FrameId>` |
| `node_store_.erase(it)` | `node_store.remove(&k)` |

## Learn more
- [`Iterator::min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key) · [`Iterator::filter`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter) · C++ [`std::min_element`](https://en.cppreference.com/w/cpp/algorithm/min_element)
