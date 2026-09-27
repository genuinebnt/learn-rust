Implement `map`, `map_err` and `and_then` on `MyResult<T, E>`, and a macro `try_my!(expr)`
that evaluates to the value on `Ok` and otherwise returns `MyResult::Err(From::from(e))` from
the enclosing function, like `?`.
