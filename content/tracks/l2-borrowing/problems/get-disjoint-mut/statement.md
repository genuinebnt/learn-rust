Write `settle`, which applies N balance changes at once or none at all, and `transfer` in terms of it.
You need `&mut` to N accounts of one slice at the same time; std's `slice::get_disjoint_mut` checks
the indices and hands them out. No `unsafe`, no cloning the balances.
