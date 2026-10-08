**Where this fits.** A frame in use (pinned) must not be evicted. The buffer pool tells the replacer with `set_evictable(frame, false/true)`.

## The task

Implement `set_evictable(frame, evictable)` in `src/buffer/lru_k_replacer.rs`: change the frame's flag and keep `curr_size` (the number of evictable frames) correct. A frame the replacer has never seen is ignored. Setting a flag to the value it already has changes nothing (and must not skew the count).

## Tests

- Of frames 1..6 with 1..5 set evictable and 6 not, `size()` is 5.
- Setting `true` twice counts once; toggling goes up and down; an unknown frame is ignored; further accesses keep the flag.

## Syntax and methods

```rust
let Some(node) = self.node_store.get_mut(&frame) else { return };   // get_mut: Option<&mut V>
if node.is_evictable != evictable { /* update flag and count together */ }
```

## Notes

`curr_size` is **derived state**: it could be computed by counting nodes. Keeping a counter is faster (`size()` is called often) but means *every* place that changes a flag, or removes a node, must update it. The two classic bugs: counting a no-op change, and forgetting it in `evict`/`remove`. When you feel the urge to cache a count, write the test that checks the cache against a recount (stage 6's model test does).

## In BusTub

"Set the evictable status of a frame. Note that replacer's size is the number of evictable frames. If a frame was previously evictable and is to be set to non-evictable, then size should decrement. If a frame was previously non-evictable and is to be set to evictable, then size should increment." (`SetEvictable` comment)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = node_store_.find(id); if (it == node_store_.end()) return; it->second.is_evictable_ = ...` | `let Some(node) = self.node_store.get_mut(&id) else { return };` |
| `size_t curr_size_` decremented below zero: wraps to 18446744073709551615 | `usize` underflow panics in debug builds (use the invariant, not `wrapping_sub`) |
| `bool` flags mutated through public members | private fields + methods |

## Learn more
- [`HashMap::get_mut`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.get_mut) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)
