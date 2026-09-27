`IntervalMap<V>` stores non-overlapping half-open intervals `[start, end)`. `insert` refuses empty
or overlapping intervals and hands the value back in `Err`. `get(point)` returns the value of the
interval containing `point`.
