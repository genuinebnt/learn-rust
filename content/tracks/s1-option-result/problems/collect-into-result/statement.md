An item is good if it parses as an `i32`; a bad item's error is `"bad number: <item>"`. Write:

- `parse_all`: every value, or the first error.
- `sum_all`: the sum as an `i64`, or the first error, without building a `Vec`.
- `parse_every_error`: every value, or **every** error, in order.
- `validate`: calls `check` on each item in order and returns its first error. Items after that error must
  not be checked.
