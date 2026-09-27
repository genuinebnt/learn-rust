Build a `MedianFinder` over a multiset of numbers:

- `add_num(num)` adds one copy of `num`;
- `remove_num(num)` removes one copy of `num` and returns `true`, or returns `false` if there is none;
- `find_median()` returns the median of the numbers currently held, or `None` when there are none.
  With an even count it's the mean of the two middle values (so it can end in `.5`).

Every operation must be O(log n) amortized.
