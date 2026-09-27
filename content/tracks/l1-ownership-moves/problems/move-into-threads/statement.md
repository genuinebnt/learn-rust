Two ways to sum in parallel:

- `sum_chunks` owns its chunks: sum each on a `thread::spawn`ed thread and return the totals in chunk
  order.
- `sum_parts` only borrows `data`, so `thread::spawn` can't use it. Split it into `parts` contiguous
  pieces whose lengths differ by at most one, longer pieces first (10 items in 3 parts: 4, 3, 3), and
  sum each piece on its own **scoped** thread. Return the sums in order. `parts` is at least 1 and may be
  larger than `data.len()`, which gives empty pieces.

Start every thread before joining any of them.
