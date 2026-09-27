Nothing here compiles: `Store` is used as `dyn Store`, but it isn't dyn-compatible. Fix it so every store
works behind `Box<dyn Store>`. Callers pass values by reference, any `Display` type: `store.put("n", &5)`.
