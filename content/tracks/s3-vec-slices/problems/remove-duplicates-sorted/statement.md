`v` is sorted in ascending order.

- `dedup_keep(v, k)`: move the values to the front so that each distinct value appears at most `k` times
  (`k ≥ 1`), keeping them in order, and return how many values that is. What's left after them doesn't
  matter. O(n) time, O(1) extra space.
- `dedup_keep_vec(v, k)`: the same on a `Vec`, which ends up holding exactly those values.
