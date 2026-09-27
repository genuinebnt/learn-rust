Each function returns `impl Iterator`, and each says the wrong thing about what the hidden iterator
borrows. `long_words` and `pairs` don't compile; `sorted_snapshot` compiles but claims to borrow `v`,
so the tests (which change `v` while the snapshot is alive) don't. Fix only the return types.
