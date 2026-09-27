Two problems:

- `Money` has no `Display`. Print dollars with a comma every three digits and two decimals: `123456` →
  `$1,234.56`, `-50` → `-$0.50`. Any `i64` is allowed. Width and alignment must work: `{:>10}`.
- The derived `Debug` on `Credentials` writes the password into the logs. Write `Debug` by hand so the
  password shows as `"***"` and everything else, including `{:#?}`, looks exactly as derived.

Keep the other derives.
