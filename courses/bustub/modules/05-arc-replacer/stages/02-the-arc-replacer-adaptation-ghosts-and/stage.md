This stage has 5 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · A hit on a live frame moves it to mfu

**Where this fits.** The "frequently used" half of the policy.

### The task

In `record_access` (`src/buffer/arc_replacer.rs`), before treating a call as a new page: if `frame` is already **live**, this is a hit. A frame on `mru` moves to the newest end of `mfu`; a frame already on `mfu` moves to its newest end. Its evictable flag is unchanged.

### Tests

- Frames 1..4 evictable, then a hit on frame 1: victims come out 2, 3, 4, 1 (mfu is evicted last while `p = 0`).
- Hits within `mfu` refresh the order: after hits on 1, 2, 1, the mfu order is 2 then 1.
- A hit keeps the flag. The start of BusTub's `SampleTest`.

### Syntax and methods

```rust
if let Some(alive) = self.alive.get(&frame) {
    let (status, handle) = (alive.status, alive.handle);      // copy out what you need, so the borrow of `self.alive` ends
    ...
    return;
}
self.mfu.move_to_back(handle);   // O(1), keeps the handle valid
```

### Notes

The borrow checker will complain if you keep `alive` (a reference into `self.alive`) while calling `self.mru.remove(..)`: they are different fields, which Rust does allow, *but* as soon as a method call takes `&mut self` it borrows everything. Copy the two small values out (`status`, `handle` are `Copy`) and the problem goes away. Use direct field access (`self.mru.remove`) over `&mut self` helper methods inside such blocks.

### In BusTub

"Case I: the page is in mru or mfu (a hit): move it to the front of mfu."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `mru_.erase(it); mfu_.push_front(frame_id);` with a stored iterator `it` | `self.mru.remove(handle); self.mfu.push_back(frame)` (a new handle: store it) |
| `mfu_.splice(mfu_.begin(), mfu_, it)` for a move within a list | `move_to_back(handle)` |
| keeping `status` as a field inside a `shared_ptr<FrameStatus>` that both lists refer to | the status and handle live in the map entry; update them together |

### Learn more
- The Rust Book: [references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) · [struct field borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html)

## Part 2 · A ghost hit raises the target, and eviction obeys it

**Where this fits.** The adaptive part of ARC.

### The task

In `src/buffer/arc_replacer.rs`:
1. In `record_access`, when the page is not on a live frame but **is a ghost on `mru_ghost`**: remove the ghost, **raise the target** `p` by `delta`, and bring the page back as a live frame (the frame passed in) at the newest end of **`mfu`**, not evictable. `delta` is `1` if `mru_ghost` is at least as long as `mfu_ghost`, otherwise `mfu_ghost.len() / mru_ghost.len()` (compute it *before* removing the hit ghost). `p` never exceeds `c`, the number of frames.
2. In `evict`, choose the side by the target: take from `mru` first if it holds **at least `p` live frames** (pinned ones count), otherwise from `mfu` first; if the preferred list has no evictable frame, use the other.

### Tests

- A page evicted and re-accessed comes back on `mfu` (it is evicted after the `mru` frames).
- An unseen page is **not** a ghost hit (BusTub: "this should NOT be a hit on ghost list since we've never seen page 7").
- BusTub's `SampleTest` up to "mru is smaller than target, mfu is victimized": `p` goes 0 → 1 → 3 through two ghost hits, then eviction switches side.
- If the preferred side has nothing evictable, the other is used.

### Syntax and methods

```rust
let delta = if self.mru_ghost.len() >= self.mfu_ghost.len() { 1 } else { self.mfu_ghost.len() / self.mru_ghost.len() };
self.mru_target_size = (self.mru_target_size + delta).min(self.replacer_size);
let order = if self.mru.len() >= self.mru_target_size { [ArcStatus::Mru, ArcStatus::Mfu] } else { [ArcStatus::Mfu, ArcStatus::Mru] };
```

### Notes

Integer division by zero: `mfu_ghost.len() / mru_ghost.len()` is only evaluated in the branch where `mru_ghost` is *shorter* than `mfu_ghost`, hence non-zero, because it contains the ghost that was just hit. The branch structure makes that safe; a rewrite with `max(1, a / b)` would divide by zero when `mru_ghost` is empty. (Rust panics on integer division by zero; C and C++ have **undefined behaviour**, usually a crash from `SIGFPE`.)

### In BusTub

"Case II: the page is in mru_ghost: adapt the target: p = min(p + delta, c), delta = 1 if |B1| >= |B2| else |B2| / |B1|. Move the page to the front of mfu."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min(a, b)` | `a.min(b)` (method on `Ord`) |
| `a / b` with `b == 0`: undefined behaviour | panics ("attempt to divide by zero") in every build |
| `size_t` arithmetic that underflows (`p - delta`) wraps to a huge number | `usize` subtraction panics in debug; use `saturating_sub` when 0 is the answer |
| `if (a >= b) {...} else {...}` | `if a >= b { .. } else { .. }` as an expression |

### Learn more
- ARC paper, section III.B ("Adaptation") · [`usize::saturating_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.saturating_sub) · [`Ord::min`](https://doc.rust-lang.org/std/cmp/trait.Ord.html#method.min)

## Part 3 · A hit on mfu_ghost lowers the target

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

## Part 4 · Keep the ghost lists bounded

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

## Part 5 · remove: delete without leaving a ghost

**Where this fits.** When a page is *deleted* (not merely evicted), the buffer pool calls `remove`: the page is gone for good, so it must not become a ghost.

### The task

Implement `remove(frame)` in `src/buffer/arc_replacer.rs`: drop an **evictable** live frame from its list and the map and lower `curr_size`, creating **no ghost**. Unknown frames (including a frame already removed) are ignored. A frame that is **not evictable** is a caller bug: panic with a message containing "not evictable".

### Tests

- Remove from the middle of `mru` or from `mfu`: the rest keep their order.
- **No ghost:** if frame 0 (page 30) were evicted, re-accessing page 30 would be a ghost hit (`mfu`, `p` up). After `remove` it is a new page and lands behind the others in `mru`.
- Double remove and unknown frames are no-ops; a removed frame can hold another page; a pinned frame panics.

### Syntax and methods

```rust
let Some(alive) = self.alive.get(&frame) else { return };
assert!(alive.evictable, "frame {} is not evictable and cannot be removed", frame.0);
```

### Notes

`evict` and `remove` differ in one line: what happens to the page id. That is the whole concept of a ghost in one sentence: *evicted-but-remembered* versus *gone*.

### In BusTub

The header comment of `Remove`: "Remove an evictable frame from replacer, along with its access history. This function should also decrement replacer's size if removal is successful. Note that this is different from evicting a frame, which always remove the frame with largest backward k-distance..."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::exception()` for a non-evictable frame | `assert!` (a bug in the caller) |
| `alive_map_.erase(frame_id)` returns a count | `remove(&k)` returns the value |
| a removal path and an eviction path that must stay consistent | share helpers, as `evict` does |

### Learn more
- [`assert!`](https://doc.rust-lang.org/std/macro.assert.html) and [`debug_assert!`](https://doc.rust-lang.org/std/macro.debug_assert.html) · [`unreachable!`](https://doc.rust-lang.org/std/macro.unreachable.html)
