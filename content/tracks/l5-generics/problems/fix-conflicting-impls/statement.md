`describe()` should work on the integer and float types, `bool`, `char`, `str`, `String`, `Name`, references to
any of these, and `Vec<T>` / `Option<T>` of anything describable (nested too). Other crates must be able to
implement `Describe` for their own types, even ones that already implement `Display`; the tests do.

It doesn't compile. Keep every output format as it is.
