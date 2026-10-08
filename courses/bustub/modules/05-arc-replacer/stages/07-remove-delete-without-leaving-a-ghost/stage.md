**Where this fits.** When a page is *deleted* (not merely evicted), the buffer pool calls `remove`: the page is gone for good, so it must not become a ghost.

## The task

Implement `remove(frame)` in `src/buffer/arc_replacer.rs`: drop an **evictable** live frame from its list and the map and lower `curr_size`, creating **no ghost**. Unknown frames (including a frame already removed) are ignored. A frame that is **not evictable** is a caller bug: panic with a message containing "not evictable".

## Tests

- Remove from the middle of `mru` or from `mfu`: the rest keep their order.
- **No ghost:** if frame 0 (page 30) were evicted, re-accessing page 30 would be a ghost hit (`mfu`, `p` up). After `remove` it is a new page and lands behind the others in `mru`.
- Double remove and unknown frames are no-ops; a removed frame can hold another page; a pinned frame panics.

## Syntax and methods

```rust
let Some(alive) = self.alive.get(&frame) else { return };
assert!(alive.evictable, "frame {} is not evictable and cannot be removed", frame.0);
```

## Notes

`evict` and `remove` differ in one line: what happens to the page id. That is the whole concept of a ghost in one sentence: *evicted-but-remembered* versus *gone*.

## In BusTub

The header comment of `Remove`: "Remove an evictable frame from replacer, along with its access history. This function should also decrement replacer's size if removal is successful. Note that this is different from evicting a frame, which always remove the frame with largest backward k-distance..."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::exception()` for a non-evictable frame | `assert!` (a bug in the caller) |
| `alive_map_.erase(frame_id)` returns a count | `remove(&k)` returns the value |
| a removal path and an eviction path that must stay consistent | share helpers, as `evict` does |

## Learn more
- [`assert!`](https://doc.rust-lang.org/std/macro.assert.html) and [`debug_assert!`](https://doc.rust-lang.org/std/macro.debug_assert.html) · [`unreachable!`](https://doc.rust-lang.org/std/macro.unreachable.html)
