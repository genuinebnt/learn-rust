A data file has one integer per line; blank lines and lines starting with `#` (after trimming) are ignored.
Write:

- `parse_optional`: `None` is `Ok(None)`, a number is `Ok(Some(n))`, anything else is the parse error.
- `parse_line`: `Ok(None)` for a blank or comment line, `Ok(Some(n))` for a number (trimmed), else the error.
- `parse_file`: every number in order, or `Err((line, error))` for the first bad line, numbered from 1.
