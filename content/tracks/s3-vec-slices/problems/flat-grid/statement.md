Store a `w × h` grid of bytes in one `Vec<u8>`. `get` and `set` return `None` / `false` out of
bounds; `row(y)` returns that row as a slice.
