**Where this fits.** The "frequently used" half of the policy.

## The task

In `record_access` (`src/buffer/arc_replacer.rs`), before treating a call as a new page: if `frame` is already **live**, this is a hit. A frame on `mru` moves to the newest end of `mfu`; a frame already on `mfu` moves to its newest end. Its evictable flag is unchanged.

## Tests

- Frames 1..4 evictable, then a hit on frame 1: victims come out 2, 3, 4, 1 (mfu is evicted last while `p = 0`).
- Hits within `mfu` refresh the order: after hits on 1, 2, 1, the mfu order is 2 then 1.
- A hit keeps the flag. The start of BusTub's `SampleTest`.

## Syntax and methods

```rust
if let Some(alive) = self.alive.get(&frame) {
    let (status, handle) = (alive.status, alive.handle);      // copy out what you need, so the borrow of `self.alive` ends
    ...
    return;
}
self.mfu.move_to_back(handle);   // O(1), keeps the handle valid
```

## Notes

The borrow checker will complain if you keep `alive` (a reference into `self.alive`) while calling `self.mru.remove(..)`: they are different fields, which Rust does allow, *but* as soon as a method call takes `&mut self` it borrows everything. Copy the two small values out (`status`, `handle` are `Copy`) and the problem goes away. Use direct field access (`self.mru.remove`) over `&mut self` helper methods inside such blocks.

## In BusTub

"Case I: the page is in mru or mfu (a hit): move it to the front of mfu."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `mru_.erase(it); mfu_.push_front(frame_id);` with a stored iterator `it` | `self.mru.remove(handle); self.mfu.push_back(frame)` (a new handle: store it) |
| `mfu_.splice(mfu_.begin(), mfu_, it)` for a move within a list | `move_to_back(handle)` |
| keeping `status` as a field inside a `shared_ptr<FrameStatus>` that both lists refer to | the status and handle live in the map entry; update them together |

## Learn more
- The Rust Book: [references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) · [struct field borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html)
