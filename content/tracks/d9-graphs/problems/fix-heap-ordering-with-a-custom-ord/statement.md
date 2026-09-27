`run_order` should return job names cheapest first, ties alphabetically. It compiles but returns the
wrong order. Fix the trait impls, not `run_order`, and don't use `Reverse`.
