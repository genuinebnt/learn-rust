The eviction rule of LRU-K in full: of the **evictable** frames, evict the one with the largest backward k-distance; among frames with infinite distance (fewer than K accesses) evict the one whose *earliest* access is oldest; remember nothing about a frame once it is gone. You first write it as a plain scan over all frames, which is easy to get right, then add `set_evictable` and `remove`, which decide *which* frames are candidates at all.

This version is O(n) per eviction on purpose. It is the **specification**; the next stage makes it fast, and its model test compares against this one.

## Part 1 · set_evictable: which frames may go

**Where this fits.** A frame in use (pinned) must not be evicted. The buffer pool tells the replacer with `set_evictable(frame, false/true)`.

### The task

Implement `set_evictable(frame, evictable)` in `src/buffer/lru_k_replacer.rs`: change the frame's flag and keep `curr_size` (the number of evictable frames) correct. A frame the replacer has never seen is ignored. Setting a flag to the value it already has changes nothing (and must not skew the count).

### Tests

- Of frames 1..6 with 1..5 set evictable and 6 not, `size()` is 5.
- Setting `true` twice counts once; toggling goes up and down; an unknown frame is ignored; further accesses keep the flag.

### Syntax and methods

```rust
let Some(node) = self.node_store.get_mut(&frame) else { return };   // get_mut: Option<&mut V>
if node.is_evictable != evictable { /* update flag and count together */ }
```

### Notes

`curr_size` is **derived state**: it could be computed by counting nodes. Keeping a counter is faster (`size()` is called often) but means *every* place that changes a flag, or removes a node, must update it. The two classic bugs: counting a no-op change, and forgetting it in `evict`/`remove`. When you feel the urge to cache a count, write the test that checks the cache against a recount (stage 6's model test does).

### In BusTub

"Set the evictable status of a frame. Note that replacer's size is the number of evictable frames. If a frame was previously evictable and is to be set to non-evictable, then size should decrement. If a frame was previously non-evictable and is to be set to evictable, then size should increment." (`SetEvictable` comment)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = node_store_.find(id); if (it == node_store_.end()) return; it->second.is_evictable_ = ...` | `let Some(node) = self.node_store.get_mut(&id) else { return };` |
| `size_t curr_size_` decremented below zero: wraps to 18446744073709551615 | `usize` underflow panics in debug builds (use the invariant, not `wrapping_sub`) |
| `bool` flags mutated through public members | private fields + methods |

### Learn more
- [`HashMap::get_mut`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.get_mut) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Part 2 · evict: the least recently used among the infinite

**Where this fits.** The point of the whole module: choosing a victim.

### The task

In `src/buffer/lru_k_replacer.rs`, implement `evict()` and the pieces it needs (`pick_victim` and `remove_node` are the suggested helpers):
- among the **evictable** frames, choose the victim: for now, treat every frame as if it had fewer than `k` accesses, so the victim is the frame whose **first** (oldest kept) access is oldest: LRU;
- remove its node (history gone, `curr_size` down by one) and return it;
- `None` if no frame is evictable (and change nothing).

### Tests

- One access each: victims in order of access. Frames not made evictable are skipped, and `evict` on them gives `None`. `evict` lowers `size`; a failed `evict` does not.
- **An evicted frame starts over:** when it is recorded again it is a new frame, not evictable until marked. With `k = 3`, frames with 1 and 2 accesses are both "infinite": the older **first** access goes first, not the older latest one.

### Syntax and methods

```rust
self.node_store.values().filter(|n| n.is_evictable()).min_by_key(|n| n.first_timestamp()).map(|n| n.frame_id())
let victim = self.pick_victim()?;                         // `?` on Option: return None if there is no victim
self.node_store.remove(&victim)                           // HashMap::remove -> Option<V>
```

### Notes

`Iterator::min_by_key` scans everything: this is O(n) per eviction, which is fine for the tests and wrong for a pool of a million frames (stage 8 fixes that). Write the obviously-correct version first; the test suite then protects the fast one.

### In BusTub

"Find the frame with largest backward k-distance and evict that frame. Only frames that are marked as 'evictable' are candidates for eviction. ... Successful eviction of a frame should decrement the size of replacer and remove the frame's access history."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min_element(first, last, comp)` returns an iterator; `end()` when empty (dereferencing it is UB) | `min_by_key(..)` returns `Option` |
| a hand-written loop with a "best so far" variable and a `bool found` | `filter` + `min_by_key` + `map` |
| `std::optional<frame_id_t> Evict()` | `Option<FrameId>` |
| `node_store_.erase(it)` | `node_store.remove(&k)` |

### Learn more
- [`Iterator::min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key) · [`Iterator::filter`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter) · C++ [`std::min_element`](https://en.cppreference.com/w/cpp/algorithm/min_element)

## Part 3 · evict: infinite distances first, then the oldest k-th access

**Where this fits.** Frames that have been accessed `k` times now compete properly.

### The task

Change the victim choice in `src/buffer/lru_k_replacer.rs` to the real rule: a frame with fewer than `k` accesses (distance +infinity) beats any frame with `k` accesses; among the infinite ones the **oldest first access** goes first; among the finite ones the **oldest k-th most recent access** goes first (that is the largest backward k-distance).

### Tests

- A one-access frame is evicted before a two-access frame (k = 2). Two full histories: the older k-th access goes first, even if the other frame was touched more recently overall. Frame 1 touched most recently overall but with an old 2nd-latest access is still evicted before frame 2 (plain LRU would keep frame 1).
- The walkthrough from BusTub's sample test, step by step. A **model test**: 30 seeded random workloads (varying k = 1..3) agree, evict by evict, with a slow reference that recomputes everything from the full access log.

### Syntax and methods

```rust
.min_by_key(|n| match n.kth_timestamp() {
    None => (0, n.first_timestamp()),        // infinite: group 0, ordered by first access
    Some(t) => (1, Some(t)),                 // finite: group 1, ordered by the k-th access
})
```

### Notes

A tuple key sorts lexicographically, so `(0, ..)` comes before `(1, ..)`: **encode a multi-level priority as a tuple**. The trap this avoids is `Option`'s own ordering: `None < Some(_)`, which would put the infinite frames first by accident *here*, and the wrong way round if you ever compare distances rather than timestamps. Make the intent explicit.

The two other ties: two frames can't have the same timestamp (the clock advances on every access), so no further tie-break is needed. (Stage 8's ordered set adds the frame id to its key anyway, so equal keys can coexist.)

### In BusTub

"Backward k-distance is computed as the difference in time between current timestamp and the timestamp of kth previous access. A frame with less than k historical references is given +inf as its backward k-distance. When multiple frames have +inf backward k-distance, the replacer evicts the frame with the earliest timestamp overall."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a comparator `[](auto &a, auto &b) { if (a.inf != b.inf) return a.inf; ... }` passed to `std::min_element` | a key function returning a tuple (or implement `Ord`) |
| `std::pair`/`std::tuple` compare lexicographically with `operator<` | tuples are `Ord` lexicographically |
| `std::numeric_limits<size_t>::max()` as the "infinite" distance | `None`, or a group number as here |
| sorting floating-point keys needs care with NaN | `f64` isn't `Ord`; use integers or `total_cmp` |

### Learn more
- [`Ord` and lexicographic tuple ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html) · [`min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key)
- The LRU-K [paper](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p297-o_neil.pdf), section 2 (the definition) and the "correlated reference period" idea BusTub leaves out

## Part 4 · remove: take a frame out of the replacer

**Where this fits.** When the buffer pool deletes a page, its frame leaves the replacer without being "evicted".

### The task

Implement `remove(frame)` in `src/buffer/lru_k_replacer.rs`: drop an **evictable** frame and its history, whatever its distance. A frame the replacer doesn't hold is ignored. Removing a frame that is **not evictable** is a bug in the caller: panic with a message containing "not evictable".

### Tests

- Remove frame 2 of 1, 2, 3: size 2, victims 1 then 3. Unknown frames: nothing happens. Non-evictable: panics.
- A removed frame has no history left: record it again and it is a brand-new frame. Removing every frame leaves an empty replacer.

### Syntax and methods

```rust
let Some(node) = self.node_store.get(&frame) else { return };
assert!(node.is_evictable(), "frame {} is not evictable and cannot be removed", frame.0);
```

### Notes

`remove` is `evict`'s sibling: the same bookkeeping (drop the node, lower the count) for a frame *chosen by the caller* instead of by the policy. Share the code (`remove_node`), so the count has one place to go wrong.

### In BusTub

"Remove an evictable frame from replacer, along with its access history. This function should also decrement replacer's size if removal is successful. Note that this is different from evicting a frame, which always remove the frame with largest backward k-distance. ... If Remove is called on a non-evictable frame, throw an exception. If specified frame is not found, directly return from this function."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::logic_error(..)` | `assert!(..)` / `panic!` (a bug), or return `Result` if callers can recover |
| "if not found, directly return" | `let Some(..) = .. else { return }` |
| exceptions propagate through the buffer pool and may unwind past locks | a panic poisons the mutex that was held, and the owner decides what to do |

### Learn more
- The Rust Book: [to panic! or not to panic!](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)

## Performance

`evict` as written here scans every node: **O(n)** per call. With 100 000 frames, evicting them all is about 5 · 10<sup>9</sup> node visits (several seconds), which is why the next stage exists. `set_evictable` and `remove` are one hash lookup and a counter update: O(1).

The scan is nevertheless the right *first* implementation: it is short enough to be obviously correct, and it becomes the **model** against which the fast version is tested. A slow correct oracle beats a fast unproven one.

**Measure it.** Time `evict` for 1 000, 10 000 and 100 000 frames, with every frame evictable, and confirm the cost grows linearly with the frame count (double the frames, double the time per call). Keep the numbers: you will compare them with the O(log n) version.

## Hints

### Write the ordering as a key, not as a pile of `if`s

The rule is "infinite first, then oldest": a **lexicographic** order. Express it as one key that you can pass to `min_by_key`: `(0, first_access)` for frames with fewer than K accesses and `(1, kth_access)` for the rest, since a tuple compares its first element first. A hand-written comparison with four branches is the version with a sign error; one key is the version you can check by reading it, and the next stage reuses it unchanged.

### `size()` is a counter, not a `.count()`

`size()` is called on every unpin in a real pool, so it must be O(1): keep a counter updated by `set_evictable` and by every path that removes an evictable frame. The invariant is *the counter equals the number of nodes with `evictable == true`*, and the places it breaks are the paths that remove a node: `evict`, `remove`, and re-recording an access. Add a `check()` that recomputes it by scan and call it in debug builds.

### `remove` is not `evict`

`evict` chooses a victim by the policy. `remove` takes a **named** frame out regardless of its distance, and forgets its history (so a later access starts a new history with infinite distance). It is a *precondition violation* to remove a frame that is not evictable; unknown frames are ignored. Decide which of those are panics and which are no-ops, and match the tests: the same distinction recurs in every module that has a `remove`.
