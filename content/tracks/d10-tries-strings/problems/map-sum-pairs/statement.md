`MapSum` maps lowercase keys to values.

- `insert(key, val)` sets `key` to `val`, replacing any earlier value for that key;
- `sum(prefix)` returns the total of the values of every key that starts with `prefix` (0 if none).

Values can be negative, and a sum can exceed `i32`.
