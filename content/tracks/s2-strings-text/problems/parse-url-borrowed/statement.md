Parse `scheme://host[:port][/path][?query]` into borrowed parts.

- `scheme` and `host` must be non-empty.
- `port`, if present, must be a valid `u16`.
- `path` defaults to `"/"`.
- `query` is split on `&` into `(key, value)` pairs; empty pieces are skipped, and a piece with no `=`
  has value `""`.

Return `None` for anything malformed.
