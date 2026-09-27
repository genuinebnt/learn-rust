- `tick(jobs)`: one scheduler tick. Every job uses up one retry (`retries_left` goes down by one, not below
  zero), and every job left with no retries is removed. Do it in one pass over the `Vec`.
- `merge_runs(runs)`: merge each stretch of neighbouring runs with the same `key` into the first run of the
  stretch, whose `count` becomes the stretch's total.
- `first_per_minute(events)`: events are `(seconds, name)`. In each stretch of consecutive events that fall
  in the same minute (`seconds / 60`), keep only the first.
