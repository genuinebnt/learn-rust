Every operator in this module orders rows: the sort, the top-N heap, the window function. They all need the same two things, written once: the **sort key** of a row (the values of its `ORDER BY` expressions) and a function that says which of two keys comes first, honouring `ASC`/`DESC` and `NULLS FIRST`/`NULLS LAST` for each key.

## The task

In `src/execution/execution_common.rs`:
- `generate_sort_key(tuple, order_bys, schema) -> Result<SortKey>`: evaluate each `ORDER BY` expression on the tuple, in order;
- `TupleComparator::compare_keys(&self, a: &SortKey, b: &SortKey) -> Ordering` (`compare` on whole entries, given, calls it): go through the order-by items in turn; the **first key that differs decides**; `Equal` if all are equal. For one key:
  - two NULLs are equal;
  - one NULL: it comes **first** when NULLs go first, which is the case for `NULLS FIRST`, and by default for an ascending key (NULL is the smallest value); `NULLS LAST` and a descending key (by default) put it last;
  - two values: compare them (`Value::compare_equals` then `compare_less_than`), reversed for `DESC`.

## Tests

- The key is the values of the order-by expressions (and empty for no order-by).
- Ascending, descending, and the default direction; equal keys are `Equal`.
- The first differing key decides; later keys break ties (`asc a, desc b`).
- NULL is the smallest value by default (first ascending, last descending).
- `NULLS FIRST`/`NULLS LAST` override the direction.
- Strings compare bytewise (`Zebra` before `apple`, a prefix before its extension), and the comparator orders a whole vector with `sort_by`.

## Syntax and methods

```rust
use std::cmp::Ordering;
ord.reverse()                                  // Less <-> Greater
if ord != Ordering::Equal { return ord; }      // the first key that differs decides
a.compare_equals(b) == Ok(CmpBool::True)       // Value comparisons return Result<CmpBool>
v.sort_by(|a, b| cmp.compare(a, b))            // stable
```

## Notes

**One function, three users.** The sort, the top-N and the window function each compare `SortEntry`s with this comparator. Getting `NULLS` and `DESC` right here is what makes `order by colG desc nulls first, colH nulls last` work everywhere.

**NULL is the smallest value (BusTub).** PostgreSQL treats NULL as the *largest* (last when ascending). BusTub's tests (`p3.16-sort-limit.slt`) say otherwise: `order by colH limit 3` returns NULLs first and `order by colH desc` last. The rule is "NULL is smaller than every value, and `DESC` reverses everything including that"; explicit `NULLS FIRST/LAST` is absolute.

**Keys are computed once.** A sort compares each row many times; evaluating `colA + colD - colA` inside the comparator would repeat it and could fail in the middle of the sort. `generate_sort_key` runs once per row, and the sort compares the stored keys.

**Total order.** A comparator must agree with itself: `compare(a, b)` is the reverse of `compare(b, a)`, and equal means equal for the rest of the sort. The vector test checks the sort comes out ordered.

## In BusTub

`execution_common.cpp`: `TupleComparator::operator()` ("TODO(P3): Implement the comparison method") returning `bool`, and `GenerateSortKey` ("TODO(P3): Implement this method"). `bound_order_by.h` defines `OrderByType::{INVALID, DEFAULT, ASC, DESC}` and `OrderByNullType::{DEFAULT, NULLS_FIRST, NULLS_LAST}`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bool operator()(const SortEntry &a, const SortEntry &b) const` ("a before b") | `fn compare(&self, a, b) -> Ordering` |
| `std::tie(...)` or a chain of `if (a != b) return a < b;` | `ord != Ordering::Equal` early return, or `then_with` |
| `std::sort` (unstable) vs `std::stable_sort` | `sort_by` is stable; `sort_unstable_by` is the other |
| comparing `Value`s with `CompareLessThan(...) == CmpTrue` | the same methods, with `Result` |

**Port rule:** a boolean "less than" comparator becomes an `Ordering`-returning function, which also tells you about ties.

## Learn more
- [`Ordering`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html) · [`slice::sort_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by) · PostgreSQL [ORDER BY](https://www.postgresql.org/docs/current/queries-order.html)

## Performance

Comparing two keys is a few `Value` matches per key: tens of nanoseconds. Sorting a million rows does about 20 million comparisons, so the comparator is the inner loop of the whole sort. Engines therefore encode keys into bytes (direction and NULL placement included) so that comparing is a `memcmp`.

**Measure it.** Sort 1,000,000 two-integer entries with this comparator and with a hard-coded `(a, b)` tuple comparison.

## Hints

### Descending reverses values, not NULL rules

Reverse the comparison of two non-NULL values for `DESC`. For a NULL against a value, the answer comes from where NULLs go, not from reversing; otherwise `desc nulls last` would put them first.

### Only the first difference matters

Return as soon as one key says `Less` or `Greater`. Do not combine the keys' results.

### Same type on both sides

Within one key both values have the same type (or are NULL); `compare_equals` then `compare_less_than` gives a total order for them. Do not compare with `==` on `Value`.
