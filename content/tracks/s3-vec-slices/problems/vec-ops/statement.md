Two ways to delete a batch of positions from a `Vec`. In both, `indices` may be in any order, may repeat,
and may contain positions past the end, which are ignored.

- `remove_indices(v, indices)`: keep the remaining elements in their original order. It must be
  O(n + k log k) for `n` elements and `k` indices; a loop of `v.remove(i)` is O(n·k).
- `remove_indices_unordered(v, indices)`: when order doesn't matter, remove each position with
  `swap_remove`, highest index first, and return the removed elements in that order. Whatever order is
  left after that is the expected answer.
