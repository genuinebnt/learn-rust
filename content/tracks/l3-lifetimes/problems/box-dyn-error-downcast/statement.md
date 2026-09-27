`sum_config` sums the values of `key=value` lines and reports problems as a `ConfigError` with its
line number: no `=`, or a value that doesn't parse, in which case the `ParseIntError` is the error's
*source*. Make `ConfigError` report that source (it doesn't yet), then write the functions that walk
an error chain: `bad_line`, `root_cause` and `chain`.
