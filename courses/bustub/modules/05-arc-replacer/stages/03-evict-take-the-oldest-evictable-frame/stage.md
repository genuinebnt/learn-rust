**Where this fits.** Evicting is where ghosts are born.

## The task

Implement `evict()` in `src/buffer/arc_replacer.rs` for the case `p = 0` (so far nothing raises it): take the **oldest evictable** frame of `mru` (skipping pinned frames), and if `mru` has none, of `mfu`. Remove its live entry, lower `curr_size`, and **remember its page id as a ghost** at the newest end of `mru_ghost` (for a victim from `mru`) or `mfu_ghost` (from `mfu`). Return the frame; `None` if nothing is evictable. The helpers `oldest_evictable(status)` and `push_ghost` are suggestions.

## Tests

- Frames 1..4 evictable: victims 1, 2, 3, 4, then `None`; size follows.
- A pinned frame is skipped; a failed evict changes nothing.
- An evicted frame can be reused for another page.

## Syntax and methods

```rust
list.iter().copied().find(|frame| self.alive[frame].evictable)   // IndexList::iter, then the first evictable one
let alive = self.alive.remove(&frame).expect("a listed frame is alive");
self.mru.remove(alive.handle);
self.ghost.insert(page_id, Ghost { status: ArcStatus::MruGhost, handle: self.mru_ghost.push_back(page_id) });
for status in [ArcStatus::Mru, ArcStatus::Mfu] { /* arrays implement IntoIterator by value */ }
```

## Notes

Eviction is the one place where a **live frame becomes a memory of a page**. Keep the three updates together (list, map, ghost) so that a frame is never in two places. The `self.alive[frame]` index panics on a missing key, which is right here: the lists and the map are supposed to agree, and a disagreement is a bug to find loudly.

## In BusTub

"Find a frame to evict ... the evicted page's id goes to the corresponding ghost list: mru → mru_ghost, mfu → mfu_ghost ... Successful eviction should decrement the size of the replacer."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (auto it = mru_.rbegin(); it != mru_.rend(); ++it) { if (alive_map_[*it]->evictable_) {...} }` (reverse iterators; `operator[]` silently inserts) | `iter().find(..)` and `self.alive[..]` (panics if absent instead of inserting) |
| erase while iterating: iterator invalidation if you continue after `erase` | find first, then remove; the borrow checker rejects mutating a list you are iterating |
| `alive_map_.erase(frame_id)` | `alive.remove(&frame)` returns the removed value |

## Learn more
- [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · [`Iterator::copied`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.copied) · The Rust Book: [`match` and enums](https://doc.rust-lang.org/book/ch06-02-match.html)
