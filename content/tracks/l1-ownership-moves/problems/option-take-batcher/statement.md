`Batcher::new(size)` groups pushed values into batches. `push` returns a full batch when one
completes; `flush` returns whatever is left, or `None` if nothing is.
