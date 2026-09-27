Implement `FromStr` for `Setting`, parsing lines like `retries = 3`. Whitespace around the key and
value is ignored. Errors: no `=` → `MissingEquals`, empty key → `EmptyKey`, value not an `i64` →
`BadValue(value)` with the trimmed value text.
