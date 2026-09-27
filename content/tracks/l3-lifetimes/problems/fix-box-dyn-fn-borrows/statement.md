Three trait objects here borrow data, but their types don't allow it, so `make_filter`, `Checks` and
`labels` don't compile. Fix the types, without copying the borrowed data. `count_passing` takes a
`&dyn Fn` that may borrow anything and is right as it is: work out why it needs no change.
