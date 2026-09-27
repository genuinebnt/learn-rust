Return the `k` points of `points` closest to the origin `(0, 0)` by Euclidean distance, nearest first.
Points at the same distance come in `(x, y)` order (smaller `x` first, then smaller `y`).
A point listed twice counts twice. If `k` is at least `points.len()`, return every point.

Coordinates can be any `i32`.
