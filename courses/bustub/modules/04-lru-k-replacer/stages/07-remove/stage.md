**Where this fits.** When the buffer pool deletes a page, its frame leaves the replacer without being "evicted".

## The task

Implement `remove(frame)` in `src/buffer/lru_k_replacer.rs`: drop an **evictable** frame and its history, whatever its distance. A frame the replacer doesn't hold is ignored. Removing a frame that is **not evictable** is a bug in the caller: panic with a message containing "not evictable".

## Tests

- Remove frame 2 of 1, 2, 3: size 2, victims 1 then 3. Unknown frames: nothing happens. Non-evictable: panics.
- A removed frame has no history left: record it again and it is a brand-new frame. Removing every frame leaves an empty replacer.

## Syntax and methods

```rust
let Some(node) = self.node_store.get(&frame) else { return };
assert!(node.is_evictable(), "frame {} is not evictable and cannot be removed", frame.0);
```

## Notes

`remove` is `evict`'s sibling: the same bookkeeping (drop the node, lower the count) for a frame *chosen by the caller* instead of by the policy. Share the code (`remove_node`), so the count has one place to go wrong.

## In BusTub

"Remove an evictable frame from replacer, along with its access history. This function should also decrement replacer's size if removal is successful. Note that this is different from evicting a frame, which always remove the frame with largest backward k-distance. ... If Remove is called on a non-evictable frame, throw an exception. If specified frame is not found, directly return from this function."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::logic_error(..)` | `assert!(..)` / `panic!` (a bug), or return `Result` if callers can recover |
| "if not found, directly return" | `let Some(..) = .. else { return }` |
| exceptions propagate through the buffer pool and may unwind past locks | a panic poisons the mutex that was held, and the owner decides what to do |

## Learn more
- The Rust Book: [to panic! or not to panic!](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)
