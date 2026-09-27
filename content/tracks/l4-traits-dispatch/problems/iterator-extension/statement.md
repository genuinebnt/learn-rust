`IterExt` adds three methods to every iterator through a blanket impl. Implement them:

- `every_nth(n)`: items 0, n, 2n, …; panics if `n` is 0. It must skip as fast as the inner iterator can:
  `(0u64..).every_nth(1_000_000_000_000)` has to be instant. Its `size_hint` must be exact whenever the
  inner one is.
- `dedup_adjacent()`: drops each item equal to the one just before it.
- `counts()`: how many times each item occurs.

The adapters are lazy: they pull only the items they need.
