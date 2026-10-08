**Where this fits.** Sorted entries can be searched in `O(log n)` page reads... or rather, entry reads. Both the hash bucket (no: unsorted) and the B+ tree page need it.

## The task

Implement `lower_bound(len, cmp)` in `src/storage/page/page_array.rs`: among the sorted entries `0..len`, the index of the **first entry that is not `Less`** than the target. `cmp` compares an entry with the target (`FnMut(&T) -> Ordering`). If every entry is less, the answer is `len`.

## Tests

- An existing entry returns its index; a missing one returns where it would go; before everything is 0, after everything is `len`; an empty range is 0.
- With duplicates, the **first** of them. Entries at or after `len` (stale bytes) are never examined.
- It works with a keyed comparator on `(GenericKey<8>, Rid)` entries, agrees with `partition_point` on 200 random arrays, and probes at most 11 entries out of 1024.

## Syntax and methods

```rust
let (mut lo, mut hi) = (0, len);
while lo < hi {
    let mid = lo + (hi - lo) / 2;                    // not (lo + hi) / 2: that overflows for huge ranges
    if cmp(&self.get(mid)) == Ordering::Less { lo = mid + 1 } else { hi = mid }
}
lo
```

## Notes

**Half-open ranges, one invariant.** `lo..hi` always contains the answer; each step halves it; when `lo == hi` that's the answer. Binary search is famous for off-by-one and overflow bugs (Java's `Arrays.binarySearch` had the `(lo + hi) / 2` overflow for years); the closure-based `lower_bound` shape avoids "found / not found" branching, so it needs no `+1`/`-1` juggling. The lookup `find` is then `lower_bound` plus one comparison.

**Why a closure.** The comparator takes the *entry* and returns how it compares to a target the caller holds: the array doesn't need to know what a key is, or how to extract it from an entry (`|(k, _)| cmp.compare(k, &target)`).

## In BusTub

```cpp
// B+ tree: "find the first key >= target"; students write it by hand or with std::lower_bound over array_ with a comparator
auto it = std::lower_bound(array_, array_ + GetSize(), key, [&](const MappingType &e, const KeyType &k) { return comparator(e.first, k) < 0; });
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::lower_bound(first, last, value, comp)` (comp = "is less") | `lower_bound(len, \|e\| e.cmp(&target))` (an `Ordering`) or `slice::partition_point(\|e\| e < target)` |
| `std::upper_bound`, `std::binary_search`, `std::equal_range` | `partition_point` with `<=`; `binary_search_by` (returns `Result<usize, usize>`) |
| `bsearch(key, base, n, size, cmp)` from `<stdlib.h>` (returns a pointer or NULL) | `binary_search_by`; no pointer |
| `(lo + hi) / 2` | `lo + (hi - lo) / 2` |

**Port rule:** `std::lower_bound` with a "less than" lambda becomes `partition_point` (on a slice) or a hand-written loop (over a page array) with an `Ordering`-returning closure.

## Learn more
- [`partition_point`](https://doc.rust-lang.org/std/primitive.slice.html#method.partition_point) · [`binary_search_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.binary_search_by) · Joshua Bloch, [Nearly All Binary Searches and Mergesorts are Broken](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
