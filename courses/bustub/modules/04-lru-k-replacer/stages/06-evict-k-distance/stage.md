**Where this fits.** Frames that have been accessed `k` times now compete properly.

## The task

Change the victim choice in `src/buffer/lru_k_replacer.rs` to the real rule: a frame with fewer than `k` accesses (distance +infinity) beats any frame with `k` accesses; among the infinite ones the **oldest first access** goes first; among the finite ones the **oldest k-th most recent access** goes first (that is the largest backward k-distance).

## Tests

- A one-access frame is evicted before a two-access frame (k = 2).
- Two full histories: the older k-th access goes first, even if the other frame was touched more recently overall. Frame 1 touched most recently overall but with an old 2nd-latest access is still evicted before frame 2 (plain LRU would keep frame 1).
- The walkthrough from BusTub's sample test, step by step.
- A **model test**: 30 seeded random workloads (varying k = 1..3) agree, evict by evict, with a slow reference that recomputes everything from the full access log.

## Syntax and methods

```rust
.min_by_key(|n| match n.kth_timestamp() {
    None => (0, n.first_timestamp()),        // infinite: group 0, ordered by first access
    Some(t) => (1, Some(t)),                 // finite: group 1, ordered by the k-th access
})
```

## Notes

A tuple key sorts lexicographically, so `(0, ..)` comes before `(1, ..)`: **encode a multi-level priority as a tuple**. The trap this avoids is `Option`'s own ordering: `None < Some(_)`, which would put the infinite frames first by accident *here*, and the wrong way round if you ever compare distances rather than timestamps. Make the intent explicit.

The two other ties: two frames can't have the same timestamp (the clock advances on every access), so no further tie-break is needed. (Stage 8's ordered set adds the frame id to its key anyway, so equal keys can coexist.)

## In BusTub

"Backward k-distance is computed as the difference in time between current timestamp and the timestamp of kth previous access. A frame with less than k historical references is given +inf as its backward k-distance. When multiple frames have +inf backward k-distance, the replacer evicts the frame with the earliest timestamp overall."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a comparator `[](auto &a, auto &b) { if (a.inf != b.inf) return a.inf; ... }` passed to `std::min_element` | a key function returning a tuple (or implement `Ord`) |
| `std::pair`/`std::tuple` compare lexicographically with `operator<` | tuples are `Ord` lexicographically |
| `std::numeric_limits<size_t>::max()` as the "infinite" distance | `None`, or a group number as here |
| sorting floating-point keys needs care with NaN | `f64` isn't `Ord`; use integers or `total_cmp` |

## Learn more
- [`Ord` and lexicographic tuple ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html) · [`min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key)
- The LRU-K [paper](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p297-o_neil.pdf), section 2 (the definition) and the "correlated reference period" idea BusTub leaves out
