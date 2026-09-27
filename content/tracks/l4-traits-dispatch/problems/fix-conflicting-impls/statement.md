The impls for `Vec<T>` and `Option<T>` don't compile next to the blanket impl (E0119: std may add
`impl Display for Vec<T>` in a future version). Keep every behaviour: the tests label `i32`, `i64`, `u64`,
`f64`, `bool`, `char`, `&str` and `String`, and `Vec`s and `Option`s of any of those, nested any way.

Types from outside the crate implement `Label` themselves.
