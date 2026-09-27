`parse_list` only parses `i32`. The tests call `parse_list::<T>(s)` for any `T: FromStr`, and expect
`ParseListError<E>` to carry `T`'s own error type: `ParseListError<ParseIntError>`,
`ParseListError<ParseBoolError>`, `ParseListError<String>`, and so on.

Keep `Display` working whenever `E` is `Display`, and `Error` (with `source()`) whenever `E` is an `Error`, so
`?` still converts it into `Box<dyn Error>`.
