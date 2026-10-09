A count-min sketch estimates how many times each item was seen, in a fixed amount of memory. It is a `depth × width` matrix of counters with one hash function per row. **Insert** adds one to the item's counter in every row; **count** returns the smallest of the item's counters. Collisions can only inflate a counter, so the estimate is never too low.

## The task

In `src/primer/count_min_sketch.rs`:

- `CountMinSketch::new(width, depth)`: `Err(Invalid)` if either is zero; otherwise `width × depth` atomic counters, all zero. (`column(row, item)`, the per-row seeded hash modulo `width`, is given.)
- `insert(&item)`: `fetch_add(1)` on the item's counter in every row (`cell(row, item)` is given).
- `count(&item)`: the minimum of the item's counters over the rows.

## Tests

- A zero width or depth is an error.
- Counts of strings and of integers (positive and negative) are exact in a sketch wide enough that nothing collides.
- Width 1 makes everything collide: the count of every item, even one never inserted, is the total.
- With one row the estimate is still never below the truth.
- Each row hashes differently but always the same way.

## Syntax and methods

```rust
self.cell(row, item).fetch_add(1, Ordering::Relaxed);                 // atomic increment through &self
(0..self.depth).map(|row| self.cell(row, item).load(Ordering::Relaxed)).min().unwrap_or(0)
(0..width as usize * depth as usize).map(|_| AtomicU32::new(0)).collect()
```

## Notes

**Why `&self`.** Counters are atomics, so the methods take a shared reference and many threads can call `insert` at once with no lock; `fetch_add` makes each increment indivisible. `Relaxed` ordering suffices because nothing else is published through the counters; threads joined before `count` is read see the final totals.

**Why the minimum, not the average.** Every counter holds the true count plus noise that is never negative. The smallest has the least noise. The average would include the noisiest rows.

**Matrix layout.** A flat vector indexed `row × width + column` keeps rows contiguous. A `Vec<Vec<..>>` would work but costs an extra indirection.

## In BusTub

`count_min_sketch.h`: "`Constructs a count-min sketch with specified dimensions`" (`@param width Number of buckets`, `@param depth Number of hash functions`) and the constructor's `@throws std::invalid_argument if width or depth are zero.`. The hash is fixed by the starter ("`PLEASE DO NOT MODIFY THE FOLLOWING`"); the course gives `column` the same role.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<std::vector<std::atomic<uint32_t>>>` | `Vec<AtomicU32>` of `depth × width` |
| `std::function<size_t(const KeyType &)>` per row | one `column(row, item)` method with the row as a seed |
| `throw std::invalid_argument` | `Err(Exception)` |

**Port rule:** `atomic<T>` fields mutated through `const` references are `AtomicT` fields mutated through `&self`.

## Learn more
- [`AtomicU32`](https://doc.rust-lang.org/std/sync/atomic/index.html) · [The paper](https://dsf.berkeley.edu/cs286/papers/countmin-latin2004.pdf)

## Performance

Insert and count cost `depth` hash computations and `depth` memory accesses, independent of how many items were seen. Memory is `4 × width × depth` bytes. An atomic increment is a few nanoseconds uncontended; contended counters (a very hot item) serialise on the cache line.

**Measure it.** Eight threads inserting one hot item: slower per operation than eight threads inserting different items.

## Hints

### Index with the row

The same item lands in a different column in every row; compute the column per row.

### Do not forget the empty case

`depth` is at least 1 after validation, so `min()` always has a value, but keep the `unwrap_or(0)` to satisfy the type.
