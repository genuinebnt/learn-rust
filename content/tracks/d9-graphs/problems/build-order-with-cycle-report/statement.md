`(a, b)` means package `a` must be built before package `b`. Return `Ok(order)`: when several packages
are ready, build the smallest number first. If some packages can never be built, return `Err` with all
of them, ascending.
