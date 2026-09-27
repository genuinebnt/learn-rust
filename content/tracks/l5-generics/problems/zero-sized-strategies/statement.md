`SortedVec<T, O>` keeps its items sorted by the strategy `O`, a zero-sized type: `Asc` (the default, so
`SortedVec<T>` means ascending) or `Desc`, or one the caller defines. Because `O` is a type, a
`SortedVec<i32, Desc>` is exactly as big as a `Vec<i32>`.

- `insert` puts `x` **after** any items that compare equal to it, in O(log n) comparisons.
- `contains` says whether some item compares equal to `x` under `O`, in O(log n).
- `reorder::<O2>()` re-sorts into another strategy; equal items keep their relative order.
- `collect()` builds one by inserting each item in turn.
