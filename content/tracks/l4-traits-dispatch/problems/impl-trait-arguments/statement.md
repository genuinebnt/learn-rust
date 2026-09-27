These functions take and return types that are too specific. The tests call them with arrays of `&str`,
`Vec`s, ranges, `split` iterators and capturing closures, clone what `evens` returns, and call
`evens(u64::MAX)`, so it must be lazy. `ordered` doesn't compile at all.

Change the signatures (and bodies where needed) so every call works. Keep what each function computes.
