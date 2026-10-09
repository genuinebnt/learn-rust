Sorted entries can be searched in `O(log n)` reads. `lower_bound` is the one binary search every ordered index page needs: it returns the first position whose entry is **not less than** the target. One answer does three jobs: *lookup* (is the entry at that position equal to the target?), *insert* (that position is where the new entry goes to keep the page sorted) and *range start* (the first key at or above a lower bound). A page that gets this right gets the whole B+ tree right.

> [!CHECK] `lower_bound` returns the first entry that is **not less** than the target, not "the entry equal to the target". Name the three jobs that one answer does, and say what it returns for a target larger than everything in the page, and for an empty page.
> ||Lookup (check whether the entry at that index equals the target), insert (the index where the target belongs) and the start of a range scan. For a target larger than everything it returns `len`, the position one past the last entry; for an empty page it returns 0, which is also `len`. In both cases "the position where it would go" is exactly right, and the caller checks `index < len` before reading an entry.||
>
> - What would `insert_at` need if the key were absent?
> - Why is "return the matching index or -1" a worse interface?
> - How is this different from the standard library's `binary_search`?

## The task

`PageArray::lower_bound(len, cmp) -> usize`: among the first `len` entries (which are sorted), the first index whose entry is not `Less` than the target, according to `cmp`, a closure that compares **an entry with the target** (`cmp(&entry)` returns `Less` if the entry is smaller). Returns `len` if every entry is less. Entries at or past `len` are stale bytes and must not be looked at.

The tests compare it with `partition_point` on a sorted `Vec` for random arrays (with duplicates) and targets; check that entries beyond `len` are ignored; check that inserting at the lower bound keeps an array sorted (a sorted set on a page); search `(GenericKey, Rid)` entries by key with a `KeyComparator`; and count comparisons: 1 024 entries must take at most 12.

## Your freedom

Iterative or recursive, how you pick the middle, and whether you fetch the entry once per probe. The closure gives you the comparison; what you must not do is scan.

## The Rust toolbox

**A comparison closure instead of a value.** `lower_bound(len, |entry| entry.cmp(&target))` lets the caller decide what "compare" means (by key only, by a comparator, descending) without the array knowing about keys. `impl FnMut(&T) -> Ordering` as the parameter type accepts any closure; `FnMut` rather than `Fn` lets a test count calls.

**The loop invariant.** `lo..hi` always contains the answer: every entry before `lo` is less than the target and every entry from `hi` on is not. Start with `lo = 0`, `hi = len`; while `lo < hi` look at `mid = lo + (hi - lo) / 2`; if the entry is less, `lo = mid + 1`, otherwise `hi = mid`. When they meet, that is the answer. Writing the invariant in a comment is how you avoid the classic off-by-one.

**`lo + (hi - lo) / 2`, not `(lo + hi) / 2`.** The second can overflow for huge arrays; with page-sized arrays it cannot, but the habit is free.

**`partition_point` as the oracle.** `slice::partition_point(|x| x < &target)` is the standard library's lower bound; the tests use it, and you can use it to check your own code against any array.

**Return a position, not an `Option`.** `Ok(i)` / `Err(i)` from `binary_search` splits "found" from "where it would go" and drops information when there are duplicates; one number serves all three jobs.

## If this is new

- [S3 Vec & slices](/t/s3-vec-slices): `binary_search`, `partition_point`, iterators over slices.
- [L5 Generics & associated types](/t/l5-generics): closures as parameters (`impl FnMut`).
- [P3 Binary search practice](/t/p3-binary-search-practice) (the practice track): the standard variants, `lower_bound` among them.
- [D4 Binary search](/t/d4-binary-search): Binary search: the lower-bound loop and its invariant.

## Tests

- `lower_bound` equals `partition_point` for random sorted arrays with duplicates and any target.
- Entries past `len` are not searched.
- Inserting at the lower bound keeps an array sorted.
- Searching `(GenericKey, Rid)` entries by key through a comparator finds the right entry.
- A target larger than everything gives `len`; smaller than everything gives 0; an empty array gives 0.
- Binary search on 1 024 entries makes at most 12 comparisons.

## Hints

### Draw the invariant

Write `lo` and `hi` under a sorted row of eight numbers and run the loop by hand for a target in the middle, then for the first and last positions, then for a target present twice.

### Duplicates

If three entries equal the target, which one must be returned? (The first.) Which branch of your loop moves `hi` when the entry equals the target?

### The count test fails

If you made more than ~11 comparisons for 1 024 entries you are scanning part of the range, or calling the closure twice per probe. Count calls in your own test.

## Performance

`log2(n)` probes: 9 for a leaf of 500 entries. Each probe decodes one entry from the page, a cache miss at worst. A B+ tree of height 3 does about 27 probes to find any of a hundred million keys.

**Measure it.** Time one million `lower_bound` calls on a 500-entry `(GenericKey<8>, Rid)` array against a linear scan. At what size does the linear scan stop being faster?

## Experiment

Optional. Predict first, then run.

1. **Branch-free.** Rewrite the loop so the `if` becomes arithmetic on `lo`/`hi`. Does it measure faster on your machine?
2. **Interpolation.** For uniformly distributed integer keys, guess the position from the key's value. How many probes does it save on average, and what happens on skewed data?

## Other designs

- **Binary search on the encoded page (ours).** Decode one entry per probe.
- **Linear scan.** Faster below ~16 entries; the crossover is machine-dependent.
- **Eytzinger layout.** Reorders entries for cache-friendly search; makes inserts hard.
- **Galloping / exponential search.** Better when the target is likely near the start.

## In BusTub

BusTub leaves the search to the student: B+ tree leaf pages binary search the keys with the comparator, as do internal pages (finding the child to descend into).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::lower_bound(begin, end, key, comp)` | `array.lower_bound(len, \|e\| comparator.compare(e, &key))` |
| `comp(a, b)` returns `bool` "a < b" | the closure returns an `Ordering` |
| iterator arithmetic | indices |

**Port rule:** `std::lower_bound` with a "less than" predicate becomes a position-returning function with a three-way comparison.

## Learn more

- [`slice::partition_point`](https://doc.rust-lang.org/std/primitive.slice.html#method.partition_point) · [`slice::binary_search_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.binary_search_by)
- [Binary search on Wikipedia](https://en.wikipedia.org/wiki/Binary_search_algorithm) (the lower-bound and upper-bound variants)
