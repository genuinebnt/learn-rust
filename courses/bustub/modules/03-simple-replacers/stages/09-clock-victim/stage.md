**Where this fits.** The hand at work.

## The task

Implement `victim()` in `src/buffer/clock_replacer.rs`: look at the frame under the `hand`. If its reference bit is **set**, clear it and move the hand to the next frame (wrapping to the start); if it is **clear**, remove that frame from the ring and return it, leaving the hand on whatever follows it. An empty ring gives `None`. (A ring whose bits are all set takes one full lap to clear them, then returns the frame the hand started on.)

## Tests

- Frames 1..4 all unpinned: victims 1, 2, 3, 4, then `None`.
- **Second chance:** after victim 1, unpin 2 again: the next victim is **3**, then 4, then 2.
- A new frame joins at the end; a lone frame with its bit set is still evicted; an empty ring is `None`.

## Syntax and methods

```rust
loop {
    if self.ring[self.hand].1 {
        self.ring[self.hand].1 = false;
        self.hand = (self.hand + 1) % self.ring.len();
    } else {
        let (frame, _) = self.ring.remove(self.hand);   // Vec::remove shifts the tail left: the hand now points at the successor
        if self.hand >= self.ring.len() { self.hand = 0; }
        return Some(frame);
    }
}
```

## Notes

The loop terminates because each lap clears every bit it passes. `remove(hand)` is the neat part: after removal the element that *was* next is at `hand`, so the hand needs no adjustment except wrapping past the end. An `% len` on an empty ring would divide by zero, which is why the empty check comes first.

## In BusTub

(No reference code is given; the sample test is the contract: after the sweep, victims `1, 2, 3` and later `5, 6, 4`, where 4 had its reference bit set by a fresh `Unpin`.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `hand = (hand + 1) % ring.size();` (`% 0` is undefined behaviour in C/C++, a panic in Rust) | `% self.ring.len()` after the empty check |
| `ring.erase(ring.begin() + hand)` shifts elements, invalidating iterators at and after the position | `Vec::remove(hand)`: same shift, and the borrow checker prevents holding a reference across it |
| `while (true) { ... }` with `return` inside | `loop { ... return ... }` (a `loop` can only exit by `return`/`break`, and its type is `!` otherwise) |

## Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · [`loop`](https://doc.rust-lang.org/reference/expressions/loop-expr.html#infinite-loops)
- CMU 15-445 "Memory Management", the slides on CLOCK
