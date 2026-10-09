Sketches are useful because they combine. Two sketches with the same dimensions count two streams; adding their counters gives the sketch of both streams. And since a sketch does not remember what it counted, finding the **top k** items takes a list of candidates to rank.

## The task

In `src/primer/count_min_sketch.rs`:

- `clear()`: every counter to zero.
- `merge(&other)`: the dimension check is given (an error for different `width` or `depth`); add each of `other`'s counters to the same counter here.
- `top_k(k, candidates)`: estimate every candidate (`count`), sort by count descending with a **stable** sort (equal counts keep the candidates' order), keep the first `k`. At most `candidates.len()` pairs.

## Tests

- Clear resets every count and the sketch counts again afterwards.
- Merge adds the counts of two streams; the other sketch is unchanged.
- Merge with collisions (width 1) and incompatible dimensions (error).
- Top-k ranks candidates by count and keeps at most `k`; unseen candidates count 0 and keep their order.
- Top-k tracks a sketch that keeps counting (BusTub's dynamic test).

## Syntax and methods

```rust
for (mine, theirs) in self.counters.iter().zip(&other.counters) {
    mine.fetch_add(theirs.load(Ordering::Relaxed), Ordering::Relaxed);
}
counted.sort_by(|a, b| b.1.cmp(&a.1));   // stable
counted.truncate(k as usize);
```

## Notes

**Merge needs the same hashes.** An item's columns depend on `width` and on the row's seed. Same dimensions, same hash functions, same columns: the counters line up. Different dimensions would add unrelated counters; hence the error.

**Merging a sketch with itself.** `a.merge(&a)` doubles every counter; with atomics that is fine in Rust (both `&` are shared).

**Why stable.** The tests list candidates in an order and expect ties to keep it; Rust's `sort_by` is stable, `sort_unstable_by` is not.

## In BusTub

`count_min_sketch.h`: "`Merges the current CountMinSketch with another, updating the current sketch with combined data from both sketches.`" (`@throws std::invalid_argument if the sketches' dimensions are incompatible`) and `TopK`: "`Gets the top k items based on estimated counts from a list of candidates.`" (`@return Vector of (item, count) pairs in descending count order`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::stable_sort` with a lambda | `Vec::sort_by` (stable by default) |
| `std::vector<std::pair<KeyType, uint32_t>>` | `Vec<(K, u32)>` |

**Port rule:** Rust's `sort_by` is stable; `sort_unstable_by` is the one that is not.

## Learn more
- [`slice::sort_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by) · [Sketch mergeability](https://arxiv.org/abs/1103.0510)

## Performance

Merge is `O(width × depth)`, independent of the streams' sizes: this is why sketches are used in distributed counting (each machine sketches its share, a coordinator merges). `top_k` is `O(c log c)` for `c` candidates.

**Measure it.** Merge two 1 000 × 10 sketches built from 1 000 000 items each: milliseconds.

## Hints

### Check dimensions first

Return the error before touching any counter, so a failed merge leaves `self` unchanged.

### Candidates with the same count

Sort by count only; do not add the item as a secondary key (items need not be ordered).
