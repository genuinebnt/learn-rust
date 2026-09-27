Wrap two legacy searches and one legacy argument (don't rewrite the searches):

- `find` returns the index `legacy_find` reports, or `None` for its `-1`.
- `rfind` returns the offset `legacy_rfind` reports, or `None` for its `usize::MAX`.
- `timeout_ms` converts a timeout for a legacy `wait(ms: i64)`, where `-1` waits forever, `0` returns at once,
  and `n > 0` waits up to `n` ms. `None` means wait forever. A `Some` timeout must never become `-1` or `0`
  unless it is zero: round up to whole milliseconds, and clamp to `i64::MAX`.
