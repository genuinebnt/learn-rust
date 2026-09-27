Implement a generic `Stack<T>` backed by a `Vec<T>`: `push`, `pop`, `peek`, `peek_mut`, `len` and
`is_empty`. The last item pushed is the first one popped.

It must work for any `T`. The tests use types that aren't `Copy`, `Clone`, `Default` or `Debug`, so
don't add bounds the code doesn't need.
