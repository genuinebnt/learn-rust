None of these compiles, and each needs a different fix. `parallel_sum` returns only after its threads
finish, so it shouldn't copy anything. `count_later`'s thread may outlive the call (the caller joins
after dropping `docs`), so it can't borrow. `spawn_named`'s bounds don't promise what
`thread::Builder::spawn` needs.
