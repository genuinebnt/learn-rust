This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · ArcReplacer: four lists and a target

**Where this fits.** LRU-K needs a tuning knob (k) and still can be fooled by a workload that changes. **ARC**, the *Adaptive Replacement Cache* (Megiddo and Modha, IBM, 2003), tunes itself. BusTub's current Project 1 asks for it.

### The idea in one page

ARC keeps **four lists**:

| list | holds | meaning |
|---|---|---|
| `mru` ("T1") | live frames | seen **once** recently |
| `mfu` ("T2") | live frames | seen **at least twice** recently |
| `mru_ghost` ("B1") | page ids only | pages recently evicted from `mru` |
| `mfu_ghost` ("B2") | page ids only | pages recently evicted from `mfu` |

and one number, the target size `p` of `mru`. Evict from `mru` when it holds at least `p` frames, otherwise from `mfu`. When a page that was evicted comes back (a **ghost hit**), ARC knows it evicted from the wrong side and moves `p` towards that side: a hit on `mru_ghost` raises `p`, a hit on `mfu_ghost` lowers it. A workload that re-reads recent pages drifts to a big `mru`; one that has a hot set drifts to a big `mfu`. The ghost lists cost only page ids, no data.

### The task

`ArcReplacer` (`src/buffer/arc_replacer.rs`) is given with its data types: `ArcStatus` (which list), `Alive` (a live frame's page, flag, list and handle) and `Ghost`. They are a starting point; the tests only use `new`, `record_access`, `set_evictable`, `evict`, `remove`, `size`. Implement `new(num_frames)` (everything empty, `p = 0`, `c = num_frames`) and `size()` (the number of evictable live frames).

### Tests

- A new replacer has size 0 (also for 0 frames).

### Syntax and methods

```rust
ArcReplacer { mru: IndexList::new(), mfu: IndexList::new(), mru_ghost: IndexList::new(), mfu_ghost: IndexList::new(),
              alive: HashMap::new(), ghost: HashMap::new(), curr_size: 0, mru_target_size: 0, replacer_size: num_frames }
```

### Notes

**Why `IndexList` + a `HashMap` of handles?** Every operation needs "find this entry's place in its list, then move or remove it" in O(1): the `HashMap` gives the handle, the `IndexList` (module 1c) acts on it. BusTub does the same with `std::list` iterators in a map. The performance test at the end runs 256K frames and expects each round of 256K accesses in a couple of seconds at most.

**Orientation.** In these lists the **front is the oldest** and the **back the newest**: evict from the front, add and refresh at the back. BusTub's comments draw the lists with the freshest next to a `!`: `[<-mru_ghost-][<-mru-]![-mfu->][->mfu_ghost->]`.

### In BusTub

```cpp
std::list<frame_id_t> mru_;  std::list<frame_id_t> mfu_;  std::list<page_id_t> mru_ghost_;  std::list<page_id_t> mfu_ghost_;
std::unordered_map<frame_id_t, std::shared_ptr<FrameStatus>> alive_map_;
std::unordered_map<page_id_t, std::shared_ptr<FrameStatus>> ghost_map_;
size_t curr_size_{0};  size_t mru_target_size_{0};  size_t replacer_size_;
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<FrameStatus>` shared by a list and a map | plain structs: the map owns the status, the list owns the id, the handle ties them |
| `enum class ArcStatus { MRU, MFU, MRU_GHOST, MFU_GHOST }` | `enum ArcStatus { Mru, Mfu, MruGhost, MfuGhost }` (Rust enums can also carry data) |
| `[[maybe_unused]] size_t curr_size_{0};` to silence warnings | unused fields warn too; the crate allows them while you work |
| `DISALLOW_COPY_AND_MOVE(ArcReplacer)` | a struct isn't `Copy`/`Clone` unless you derive it; moves are the default and a moved-from value is unusable |

**Port rule:** `shared_ptr` used only to let two containers refer to one object is usually a sign to **own it in one place and refer by key/handle** from the other.

### Learn more
- Megiddo and Modha, [*ARC: A Self-Tuning, Low Overhead Replacement Cache*](https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf) (FAST 2003); [Wikipedia](https://en.wikipedia.org/wiki/Adaptive_replacement_cache)
- [OpenZFS `arc.c`](https://github.com/openzfs/zfs/blob/master/module/zfs/arc.c): ARC in production · CMU 15-445 "Memory Management" lecture

## Part 2 · record_access (new pages) and set_evictable

**Where this fits.** The first way a page enters the replacer.

### The task

In `src/buffer/arc_replacer.rs`:
- `record_access(frame, page_id)` for a frame and page the replacer has **not seen**: put the frame at the newest end of `mru`, remember its page, not evictable. (Hits and ghosts come in later stages; for now every call is a new page.)
- `set_evictable(frame, evictable)`: for a live frame, set the flag and keep `curr_size` right; ignore unknown frames; setting the same value twice changes nothing.

### Tests

- Recorded frames start non-evictable. Frames 1..6 with 1..5 evictable and 6 not: size 5.
- Setting a flag twice counts once; unknown frames are ignored; 100 new pages are fine.

### Syntax and methods

```rust
let handle = self.mru.push_back(frame);
self.alive.insert(frame, Alive { page_id, evictable: false, status: ArcStatus::Mru, handle });
let Some(alive) = self.alive.get_mut(&frame) else { return };
```

### Notes

The suggested `push_alive` helper (keep the list and the map in step in one place) is worth writing even though each call site is one line: the *pair* of updates is the invariant, and later stages add more call sites. This is the "make illegal states unrepresentable" instinct at the smallest scale.

### In BusTub

"Record access to a frame. ... If the page is not in any of the lists (case IV), it goes to the front of mru; `evictable_` defaults to false."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `alive_map_[frame_id] = std::make_shared<FrameStatus>(page_id, frame_id, false, ArcStatus::MRU);` | `self.alive.insert(frame, Alive { .. })` |
| `mru_.push_front(frame_id)` (BusTub's front is the *newest*) | `push_back` (here the back is the newest) |
| default arguments: `RecordAccess(frame_id, page_id, AccessType access_type = AccessType::Unknown)` | no default arguments in Rust: add a parameter, or a second method, or an `Option` |

### Learn more
- [`HashMap::insert`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.insert) · [`get_mut`](https://doc.rust-lang.org/std/collections/hash_map/struct.HashMap.html#method.get_mut)

## Part 3 · evict: take the oldest evictable frame, leave a ghost

**Where this fits.** Evicting is where ghosts are born.

### The task

Implement `evict()` in `src/buffer/arc_replacer.rs` for the case `p = 0` (so far nothing raises it): take the **oldest evictable** frame of `mru` (skipping pinned frames), and if `mru` has none, of `mfu`. Remove its live entry, lower `curr_size`, and **remember its page id as a ghost** at the newest end of `mru_ghost` (for a victim from `mru`) or `mfu_ghost` (from `mfu`). Return the frame; `None` if nothing is evictable. The helpers `oldest_evictable(status)` and `push_ghost` are suggestions.

### Tests

- Frames 1..4 evictable: victims 1, 2, 3, 4, then `None`; size follows.
- A pinned frame is skipped; a failed evict changes nothing.
- An evicted frame can be reused for another page.

### Syntax and methods

```rust
list.iter().copied().find(|frame| self.alive[frame].evictable)   // IndexList::iter, then the first evictable one
let alive = self.alive.remove(&frame).expect("a listed frame is alive");
self.mru.remove(alive.handle);
self.ghost.insert(page_id, Ghost { status: ArcStatus::MruGhost, handle: self.mru_ghost.push_back(page_id) });
for status in [ArcStatus::Mru, ArcStatus::Mfu] { /* arrays implement IntoIterator by value */ }
```

### Notes

Eviction is the one place where a **live frame becomes a memory of a page**. Keep the three updates together (list, map, ghost) so that a frame is never in two places. The `self.alive[frame]` index panics on a missing key, which is right here: the lists and the map are supposed to agree, and a disagreement is a bug to find loudly.

### In BusTub

"Find a frame to evict ... the evicted page's id goes to the corresponding ghost list: mru → mru_ghost, mfu → mfu_ghost ... Successful eviction should decrement the size of the replacer."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (auto it = mru_.rbegin(); it != mru_.rend(); ++it) { if (alive_map_[*it]->evictable_) {...} }` (reverse iterators; `operator[]` silently inserts) | `iter().find(..)` and `self.alive[..]` (panics if absent instead of inserting) |
| erase while iterating: iterator invalidation if you continue after `erase` | find first, then remove; the borrow checker rejects mutating a list you are iterating |
| `alive_map_.erase(frame_id)` | `alive.remove(&frame)` returns the removed value |

### Learn more
- [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · [`Iterator::copied`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.copied) · The Rust Book: [`match` and enums](https://doc.rust-lang.org/book/ch06-02-match.html)
