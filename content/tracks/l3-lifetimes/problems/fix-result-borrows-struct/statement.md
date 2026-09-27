`Index` holds slices of a text. Its methods' results are slices of that text too, but elision ties
them to `&self`, so callers can't keep them once the `Index` is gone, and `into_lines` doesn't
compile at all. Fix the four return types so each says what it really borrows. The tests drop the
`Index` and keep the results.
