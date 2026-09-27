Write three lookups into a `Json` value by a dotted path such as `"users.0.name"`:

- `get` returns the value at the path, or `None`. On an object a segment is a key (even if it looks like a
  number; the first matching key wins). On an array it's an index made of decimal digits only. Anything else,
  or a segment that goes nowhere, is `None`. The empty path is `root` itself.
- `num_at` returns the number at the path, if there is a number there.
- `is_null_at` is true only if the path exists and holds `null`. A missing path is not `null`.

None of them may panic.
