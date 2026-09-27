Three small helpers that a config or HTTP layer needs. The first two return a slice of their input;
the third edits a `String` in place.

- `extension(path)`: the extension of the last `/`-separated component. `"src/a.tar.gz"` → `Some("gz")`.
  A dot in a directory name doesn't count, a leading dot is part of the name (`".bashrc"` → `None`),
  and a trailing dot gives no extension (`"notes."` → `None`).
- `unquote(s)`: `s` without **one** pair of matching surrounding quotes, `"…"` or `'…'`. Anything else is
  returned unchanged.
- `add_param(url, key, value)`: adds `key=value` to the query string of `url`. Use `?` if the URL has no
  query yet, `&` otherwise, and no separator if the query already ends with `?` or `&`. A `#fragment`
  stays at the end, and a `?` inside the fragment doesn't start a query.
