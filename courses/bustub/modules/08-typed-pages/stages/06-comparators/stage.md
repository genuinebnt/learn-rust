**Where this fits.** An index needs to sort keys. The ordering lives in a comparator object, because the same bytes can mean different things.

## The task

`trait KeyComparator<K> { fn compare(&self, lhs: &K, rhs: &K) -> Ordering; }` is given in `src/storage/index/generic_key.rs`. Implement it for:
- `IntComparator` over `i32` (`src/storage/index/int_comparator.rs`): the numeric order;
- `GenericComparator<N>` over `GenericKey<N>`: compare the **signed integers** in their first 8 bytes.

## Tests

- `1 < 2`, `2 == 2`, `3 > -3`, `i32::MIN < i32::MAX`.
- Keys 5 < 9, 9 == 9, 10 > 9; **negative numbers sort first** (`-1 < 0`, `-100 < -2`), and `256 > 1` even though 256's first byte is 0.
- A comparator drives `sort_by` correctly.

## Syntax and methods

```rust
use std::cmp::Ordering;                 // Less | Equal | Greater
lhs.get_as_integer().cmp(&rhs.get_as_integer())     // Ord::cmp
keys.sort_by(|a, b| cmp.compare(a, b));
```

## Notes

**Comparing the bytes is a different question.** `[u8; 8]` compares lexicographically as unsigned bytes: for a little-endian integer that is neither numeric order nor signed order. A comparator exists to say what the bytes *mean*. (BusTub's real `GenericComparator` interprets the bytes through the index's schema: integer columns, varchars, ... You will build that in the Tuples module; this one covers the tests that put one integer in a key.)

**`Ordering` instead of -1/0/1.** BusTub's comparators return an `int`; callers write `cmp(a, b) < 0`. `Ordering` is an enum (`Less`, `Equal`, `Greater`) with methods (`is_lt`, `then`, `reverse`) and works with `sort_by`, `binary_search_by`, `max_by`...

## In BusTub

```cpp
class IntComparator { public: inline auto operator()(const int lhs, const int rhs) const -> int { if (lhs < rhs) return -1; if (lhs > rhs) return 1; return 0; } };
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a function object with `operator()(a, b) -> int` (-1/0/1) | `trait KeyComparator<K>` with `compare(&self, a, b) -> Ordering` |
| `std::less<K>`, `std::function<bool(K, K)>`, `qsort`'s `int (*)(const void *, const void *)` | `Ord`, `Fn(&K, &K) -> Ordering`, `sort_by` |
| comparator passed as a template parameter `typename KeyComparator` | a generic `C: KeyComparator<K>` |
| `memcmp(a, b, n)` for byte keys (unsigned lexicographic order) | `a.cmp(b)` on `[u8; N]` (the same order) |
| `<=>` (C++20 three-way comparison) | `Ord::cmp` / `PartialOrd::partial_cmp` |

**Port rule:** a C++ comparator template parameter is a trait bound with a `compare` method returning `Ordering`; if it is a plain function, accept `impl Fn(&K, &K) -> Ordering`.

## Learn more
- [`Ordering`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html) · [`Ord`](https://doc.rust-lang.org/std/cmp/trait.Ord.html) · [`sort_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by)
- BusTub [int_comparator.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/index/int_comparator.h)
