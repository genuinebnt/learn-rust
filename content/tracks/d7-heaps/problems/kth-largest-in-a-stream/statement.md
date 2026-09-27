Build a `KthLargest` that watches a stream of numbers:

- `new(k, nums)` starts the stream with the values in `nums`;
- `add(val)` adds `val` and returns the `k`-th largest value seen so far, counting duplicates
  (for `k = 1` that is the maximum).

While fewer than `k` values have arrived there is no `k`-th largest, so `add` returns `None`.
