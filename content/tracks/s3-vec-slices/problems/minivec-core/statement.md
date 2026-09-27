Build `MiniVec<T>` on a raw allocation from `std::alloc`, without using `Vec`. Implement `new`,
`push`, `pop`, `get`, `len`, `capacity` and `Drop`. Grow from 0 to 4, then double. `Drop` must drop
every remaining element and free the buffer. You don't need to support zero-sized `T`.
