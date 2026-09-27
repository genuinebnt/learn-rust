Implement `MyOption<T>`, a copy of `Option<T>`, with ten methods that behave like std's:
`is_some_and`, `unwrap_or_else`, `unwrap_or_default`, `map`, `and_then`, `and`, `or_else`, `filter`, `take`
and `iter`. `iter` returns an `Iter` that yields `&T` at most once.

Closures must run only when std's would, and at most once.
