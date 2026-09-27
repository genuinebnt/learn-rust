`deepest_mut` and `first_long_or_push` are correct and don't compile: each returns a mutable borrow from
inside a loop on one path and keeps using the same data on another. Fix both without `unsafe`, without
cloning, and without changing any signature. `grow` depends on `deepest_mut`.
