A metrics database keeps every live series in a head block. Each series stores its metric name, its
labels (sorted by name, fixed at creation) and its samples. Thousands of series share the same few
strings, the query engine takes copies of label sets that must outlive the head, and ingestion adds
series all day, so the owned-`String` representation allocates on every step.

Keep the API and change the representation:

- `size_of::<Series>()` at most **56** bytes (it's 72);
- `add_series` whose strings the head has seen before makes **exactly one** allocation, and each new
  distinct string costs exactly one more (`with_capacity` reserves room, so nothing else grows);
- `labels_of` makes **no** allocation, and its result still outlives the `Head`;
- `append` stays amortised O(1); `symbols()` is the number of distinct strings held.
