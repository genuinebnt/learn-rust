**Where this fits.** LRU-K needs a tuning knob (k) and still can be fooled by a workload that changes. **ARC**, the *Adaptive Replacement Cache* (Megiddo and Modha, IBM, 2003), tunes itself. BusTub's current Project 1 asks for it.

## The idea in one page

ARC keeps **four lists**:

| list | holds | meaning |
|---|---|---|
| `mru` ("T1") | live frames | seen **once** recently |
| `mfu` ("T2") | live frames | seen **at least twice** recently |
| `mru_ghost` ("B1") | page ids only | pages recently evicted from `mru` |
| `mfu_ghost` ("B2") | page ids only | pages recently evicted from `mfu` |

and one number, the target size `p` of `mru`. Evict from `mru` when it holds at least `p` frames, otherwise from `mfu`. When a page that was evicted comes back (a **ghost hit**), ARC knows it evicted from the wrong side and moves `p` towards that side: a hit on `mru_ghost` raises `p`, a hit on `mfu_ghost` lowers it. A workload that re-reads recent pages drifts to a big `mru`; one that has a hot set drifts to a big `mfu`. The ghost lists cost only page ids, no data.

## The task

`ArcReplacer` (`src/buffer/arc_replacer.rs`) is given with its data types: `ArcStatus` (which list), `Alive` (a live frame's page, flag, list and handle) and `Ghost`. They are a starting point; the tests only use `new`, `record_access`, `set_evictable`, `evict`, `remove`, `size`. Implement `new(num_frames)` (everything empty, `p = 0`, `c = num_frames`) and `size()` (the number of evictable live frames).

## Tests

- A new replacer has size 0 (also for 0 frames).

## Syntax and methods

```rust
ArcReplacer { mru: IndexList::new(), mfu: IndexList::new(), mru_ghost: IndexList::new(), mfu_ghost: IndexList::new(),
              alive: HashMap::new(), ghost: HashMap::new(), curr_size: 0, mru_target_size: 0, replacer_size: num_frames }
```

## Notes

**Why `IndexList` + a `HashMap` of handles?** Every operation needs "find this entry's place in its list, then move or remove it" in O(1): the `HashMap` gives the handle, the `IndexList` (module 1c) acts on it. BusTub does the same with `std::list` iterators in a map. The performance test at the end runs 256K frames and expects each round of 256K accesses in a couple of seconds at most.

**Orientation.** In these lists the **front is the oldest** and the **back the newest**: evict from the front, add and refresh at the back. BusTub's comments draw the lists with the freshest next to a `!`: `[<-mru_ghost-][<-mru-]![-mfu->][->mfu_ghost->]`.

## In BusTub

```cpp
std::list<frame_id_t> mru_;  std::list<frame_id_t> mfu_;  std::list<page_id_t> mru_ghost_;  std::list<page_id_t> mfu_ghost_;
std::unordered_map<frame_id_t, std::shared_ptr<FrameStatus>> alive_map_;
std::unordered_map<page_id_t, std::shared_ptr<FrameStatus>> ghost_map_;
size_t curr_size_{0};  size_t mru_target_size_{0};  size_t replacer_size_;
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<FrameStatus>` shared by a list and a map | plain structs: the map owns the status, the list owns the id, the handle ties them |
| `enum class ArcStatus { MRU, MFU, MRU_GHOST, MFU_GHOST }` | `enum ArcStatus { Mru, Mfu, MruGhost, MfuGhost }` (Rust enums can also carry data) |
| `[[maybe_unused]] size_t curr_size_{0};` to silence warnings | unused fields warn too; the crate allows them while you work |
| `DISALLOW_COPY_AND_MOVE(ArcReplacer)` | a struct isn't `Copy`/`Clone` unless you derive it; moves are the default and a moved-from value is unusable |

**Port rule:** `shared_ptr` used only to let two containers refer to one object is usually a sign to **own it in one place and refer by key/handle** from the other.

## Learn more
- Megiddo and Modha, [*ARC: A Self-Tuning, Low Overhead Replacement Cache*](https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf) (FAST 2003); [Wikipedia](https://en.wikipedia.org/wiki/Adaptive_replacement_cache)
- [OpenZFS `arc.c`](https://github.com/openzfs/zfs/blob/master/module/zfs/arc.c): ARC in production · CMU 15-445 "Memory Management" lecture
