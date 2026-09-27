Build `OpenMap<V>`, a hash map from `u64` keys to `V`, on one `Vec<Slot<V>>` with linear probing.
Implement `new`, `insert` (returning the old value if the key existed), `get`, `remove` and `len`.
Keep the load factor below 3/4 by doubling. Removing must not break lookups of keys further along a probe chain.
