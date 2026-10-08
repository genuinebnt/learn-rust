**Where this fits.** Pinning must not disturb where the hand points.

## The task

Implement `pin(frame)` in `src/buffer/clock_replacer.rs`: remove the frame from the ring if it is there. The `hand` must keep pointing at **the same frame it pointed at before** (if the removed frame was *before* the hand, the hand's index shifts down by one; if it was *at* the hand, the hand now points at its successor), wrapping to 0 when it falls off the end. Unknown frames: nothing happens.

## Tests

- A pinned frame leaves the ring and is never a victim; an unknown frame changes nothing.
- The scenario that breaks a careless version: frames 1..6; victim 1; unpin 2 (second chance); victim 3; **pin 2** (it lies behind the hand): the next victims must be 4, then 5. Pinning the frame under the hand moves on to its successor; pinning the last frame wraps.

## Syntax and methods

```rust
let Some(at) = self.ring.iter().position(|(f, _)| *f == frame) else { return };   // Iterator::position -> Option<usize>
self.ring.remove(at);
if at < self.hand { self.hand -= 1; }
if self.hand >= self.ring.len() { self.hand = 0; }
```

## Notes

This is an **index invalidation** bug waiting to happen, in any language: you store a position, then remove something before it. In C++ the analogue is an iterator or index kept across `erase`. Rust's borrow checker can't help with a plain `usize`; tests do. (If the hand were a reference into the `Vec`, the borrow checker *would* stop you from removing anything while it is held, which is the reason to keep it an index.)

## In BusTub

```cpp
// The sample test: Pin(3) (already victimised, a no-op), Pin(4) (removes it), then Unpin(4) sets the reference bit again.
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = std::find(...); ring.erase(it);` with an index `hand` kept elsewhere: the classic stale-index bug | `position` + `remove` + explicit fix-up of `hand` |
| `std::vector::erase` invalidates iterators/pointers/references at or after the erased element | the same data movement; `&`/`&mut` into the `Vec` can't outlive the call |
| `std::deque`, `std::list` give stable iterators across erases of *other* elements | an arena (stage 1) gives stable handles; a `Vec` ring does not |

**Port rule:** every stored index into a `Vec` is a promise that nothing before it is removed. Either use handles (generational) or fix the index up at every removal, and test it.

## Learn more
- [`Iterator::position`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position) · [`Vec::retain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.retain)
