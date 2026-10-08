**Where this fits.** The first way a page enters the replacer.

## The task

In `src/buffer/arc_replacer.rs`:
- `record_access(frame, page_id)` for a frame and page the replacer has **not seen**: put the frame at the newest end of `mru`, remember its page, not evictable. (Hits and ghosts come in later stages; for now every call is a new page.)
- `set_evictable(frame, evictable)`: for a live frame, set the flag and keep `curr_size` right; ignore unknown frames; setting the same value twice changes nothing.

## Tests

- Recorded frames start non-evictable. Frames 1..6 with 1..5 evictable and 6 not: size 5.
- Setting a flag twice counts once; unknown frames are ignored; 100 new pages are fine.

## Syntax and methods

```rust
let handle = self.mru.push_back(frame);
self.alive.insert(frame, Alive { page_id, evictable: false, status: ArcStatus::Mru, handle });
let Some(alive) = self.alive.get_mut(&frame) else { return };
```

## Notes

The suggested `push_alive` helper (keep the list and the map in step in one place) is worth writing even though each call site is one line: the *pair* of updates is the invariant, and later stages add more call sites. This is the "make illegal states unrepresentable" instinct at the smallest scale.

## In BusTub

"Record access to a frame. ... If the page is not in any of the lists (case IV), it goes to the front of mru; `evictable_` defaults to false."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `alive_map_[frame_id] = std::make_shared<FrameStatus>(page_id, frame_id, false, ArcStatus::MRU);` | `self.alive.insert(frame, Alive { .. })` |
| `mru_.push_front(frame_id)` (BusTub's front is the *newest*) | `push_back` (here the back is the newest) |
| default arguments: `RecordAccess(frame_id, page_id, AccessType access_type = AccessType::Unknown)` | no default arguments in Rust: add a parameter, or a second method, or an `Option` |

## Learn more
- [`HashMap::insert`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.insert) · [`get_mut`](https://doc.rust-lang.org/std/collections/hash_map/struct.HashMap.html#method.get_mut)
