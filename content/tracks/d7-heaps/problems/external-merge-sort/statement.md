External sorting handles data too big for memory: sort chunks into *runs* on disk, then merge the runs in
one streaming pass. Write that merge. `kmerge_by_key(runs, key)` takes iterators that each yield items in
ascending `key` order and returns an iterator over all their items in ascending `key` order.

- **Lazy:** hold at most one unreturned item per run. The tests watch how far each run has been read.
- **Stable:** equal keys come out in run order (run 0 first), and a run's own items keep their order.
- **One key per item:** call `key` exactly once for each item; keys may be expensive (think parsing a record).
- **Any item type:** items need no `Clone`, `Ord` or `Debug`; only keys are compared.
- **`size_hint`:** items held plus the runs' own hints, exact when every run's hint is exact.
