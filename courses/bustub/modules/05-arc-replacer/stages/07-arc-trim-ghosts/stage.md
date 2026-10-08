**Where this fits.** Ghost lists cost memory (a page id each) and must not grow forever.

## The task

When `record_access` sees a page that is on **no** list, before adding it to `mru` apply the paper's limits (cases 4A and 4B in the paper's Figure 4), using `c` = the number of frames:
- if `mru.len() + mru_ghost.len() >= c`: forget the **oldest** ghost of `mru_ghost` (if any);
- else if all four lists together hold at least `2c`: forget the oldest ghost of `mfu_ghost` (if any).

Forgetting a ghost removes it from its list **and** from the ghost map.

## Tests

- BusTub's `SampleTest2` from the start through "Access page 3 with frame 1, this should be a ghost hit": page 4's arrival drives ghost 1 out; page 1 then arrives as a **new** page (not a ghost hit) and drives ghost 2 out; page 3 is still a ghost.
- The whole of `SampleTest2`, end to end, including case 4B where `mfu_ghost` shrinks.

## Syntax and methods

```rust
if let Some(page) = self.mru_ghost.pop_front() { self.ghost.remove(&page); }   // IndexList::pop_front returns the oldest
```

## Notes

Two structures hold ghosts (a list for order, a map for lookup); forgetting from one without the other leaves a ghost you can no longer age out or a map entry whose handle is stale (and stale handles return `None` / `false` in `IndexList`, which then hides the bug). That is the reason the `IndexList` checks generations: it turns a silent corruption into a visible mismatch.

## In BusTub

"Case IV: the page is in none of the lists. 4A: if |T1| + |B1| == c, discard the LRU ghost in B1. 4B: otherwise if |T1| + |B1| < c and the total of the four lists == 2c, discard the LRU ghost in B2. Then add the page to the front of mru."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ghost_map_.erase(mru_ghost_.back()); mru_ghost_.pop_back();` (two calls that must stay together) | `pop_front()` then `ghost.remove(&page)` |
| `.back()` of an empty list: undefined behaviour | `Option` from `pop_front` |
| size comparisons between `size_t` and `int` | all `usize` here |

## Learn more
- ARC paper, Figure 4 (the algorithm) · BusTub's [arc_replacer_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/buffer/arc_replacer_test.cpp)
