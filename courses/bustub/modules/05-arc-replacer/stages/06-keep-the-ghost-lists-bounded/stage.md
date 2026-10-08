This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · A hit on mfu_ghost lowers the target

**Where this fits.** The mirror of the last stage.

### The task

In `record_access` (`src/buffer/arc_replacer.rs`): for a page that is a ghost on **`mfu_ghost`**: remove the ghost, **lower** `p` by `delta` (never below 0), and bring the page back on `mfu` as before. Here `delta` is `1` if `mfu_ghost` is at least as long as `mru_ghost`, otherwise `mru_ghost.len() / mfu_ghost.len()`.

### Tests

- BusTub's `SampleTest` through "p is adjusted down by 1/1 = 1": after the second eviction `p` is 3, a hit on page 1 (an `mfu_ghost`) lowers it to 2, and the next eviction takes from `mru` (page 7), skipping the pinned frame 6.
- The target stops at 0 and doesn't wrap around to a huge `usize`.

### Syntax and methods

```rust
self.mru_target_size = self.mru_target_size.saturating_sub(delta);   // 0 is the floor
```

### Notes

If your tests pass with `p` going negative-as-huge, that is `usize` underflow: in a debug build it panics, in release it wraps and the policy silently degenerates into "always evict from `mfu`". `saturating_sub` states the intent. Rust's integer overflow checking in debug builds is one of the cheapest bug-finders you get for free: leave it on in tests.

### In BusTub

"Case III: the page is in mfu_ghost: p = max(p - delta, 0), delta = 1 if |B2| >= |B1| else |B1| / |B2|. Move the page to the front of mfu."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `p = std::max<size_t>(p - delta, 0)`: the subtraction wraps *before* `max` sees it (a classic ARC port bug) | `p.saturating_sub(delta)` |
| `-fsanitize=undefined` / `-ftrapv` to catch signed overflow (unsigned wraps by definition) | debug builds panic on any overflow; `checked_*`, `wrapping_*`, `saturating_*` say what you mean |
| compare `int` with `size_t` (sign-compare warnings, surprising conversions) | no implicit conversions: the compiler makes you cast |

### Learn more
- [Integer overflow in Rust](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · [`checked_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.checked_sub)

## Part 2 · Keep the ghost lists bounded

**Where this fits.** Ghost lists cost memory (a page id each) and must not grow forever.

### The task

When `record_access` sees a page that is on **no** list, before adding it to `mru` apply the paper's limits (cases 4A and 4B in the paper's Figure 4), using `c` = the number of frames:
- if `mru.len() + mru_ghost.len() >= c`: forget the **oldest** ghost of `mru_ghost` (if any);
- else if all four lists together hold at least `2c`: forget the oldest ghost of `mfu_ghost` (if any).

Forgetting a ghost removes it from its list **and** from the ghost map.

### Tests

- BusTub's `SampleTest2` from the start through "Access page 3 with frame 1, this should be a ghost hit": page 4's arrival drives ghost 1 out; page 1 then arrives as a **new** page (not a ghost hit) and drives ghost 2 out; page 3 is still a ghost.
- The whole of `SampleTest2`, end to end, including case 4B where `mfu_ghost` shrinks.

### Syntax and methods

```rust
if let Some(page) = self.mru_ghost.pop_front() { self.ghost.remove(&page); }   // IndexList::pop_front returns the oldest
```

### Notes

Two structures hold ghosts (a list for order, a map for lookup); forgetting from one without the other leaves a ghost you can no longer age out or a map entry whose handle is stale (and stale handles return `None` / `false` in `IndexList`, which then hides the bug). That is the reason the `IndexList` checks generations: it turns a silent corruption into a visible mismatch.

### In BusTub

"Case IV: the page is in none of the lists. 4A: if |T1| + |B1| == c, discard the LRU ghost in B1. 4B: otherwise if |T1| + |B1| < c and the total of the four lists == 2c, discard the LRU ghost in B2. Then add the page to the front of mru."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `ghost_map_.erase(mru_ghost_.back()); mru_ghost_.pop_back();` (two calls that must stay together) | `pop_front()` then `ghost.remove(&page)` |
| `.back()` of an empty list: undefined behaviour | `Option` from `pop_front` |
| size comparisons between `size_t` and `int` | all `usize` here |

### Learn more
- ARC paper, Figure 4 (the algorithm) · BusTub's [arc_replacer_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/buffer/arc_replacer_test.cpp)
