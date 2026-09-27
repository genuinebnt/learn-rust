`sum_config` sums the values of `key=value` lines, skipping blank lines. A line without `=` is a
`ConfigError` with its 1-based line number; a bad number is the `ParseIntError`. Both come back as
`Box<dyn Error>`.

`bad_line` recovers the line number when the error is a `ConfigError`.
