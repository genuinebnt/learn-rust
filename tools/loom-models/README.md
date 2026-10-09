# Loom models of the course's concurrency protocols

Run: `cd tools/loom-models && RUSTFLAGS="--cfg loom" cargo test --release`

Each pair is a wrong version (marked `should_panic`: loom finds an interleaving that breaks it) and the shipped version (passes in every
interleaving): the HyperLogLog register update, the trie store's writers, commit publication order, and the write-write conflict check under
the page latch. See `courses/bustub/concepts/testing-concurrent-code-with-loom-and-miri.md`.
