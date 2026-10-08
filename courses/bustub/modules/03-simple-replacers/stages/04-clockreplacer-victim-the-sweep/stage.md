This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · ClockReplacer: the ring, unpin and size

**Where this fits.** LRU needs a list update on every access. **CLOCK** approximates LRU with one bit per frame and a sweeping hand: much cheaper, and what PostgreSQL and the Linux kernel's page cache use.

### The task

`ClockReplacer` (`src/buffer/clock_replacer.rs`) keeps a ring of `(FrameId, bool)` (the bool is the **reference bit**) and a `hand`. Implement:
- `unpin(frame)`: a frame already on the ring gets its reference bit set; a new frame is added at the **end** of the ring with its bit set. If the ring already has `capacity` frames, panic with "full";
- `size()`: how many frames are on the ring.

### Tests

- 6 unpins give size 6; unpinning twice counts once; a 2nd frame on a 1-frame replacer panics ("full").

### Syntax and methods

```rust
match self.ring.iter_mut().find(|(f, _)| *f == frame) {     // iter_mut + find: a mutable reference to the slot, if any
    Some(slot) => slot.1 = true,                              // tuple fields: .0 and .1
    None => self.ring.push((frame, true)),
}
```

### Notes

**Why CLOCK.** On a page hit, LRU must move the page in a shared list: a lock and several writes. CLOCK only sets a bit. The hand does the work later, on eviction: it gives a frame with its bit set "a second chance" by clearing the bit; the first frame whose bit is already clear is the victim. The ring can be a plain `Vec` because the hand moves forward only; searching for a frame is `O(n)` here, which is fine for the sweep and the reason real implementations store the bit inside the frame's own header.

### In BusTub

```cpp
class ClockReplacer : public Replacer { /* TODO(student): implement me! */ };
```

(BusTub gives no implementation and a single sample test; the textbook algorithm is what is expected.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `struct { frame_id_t id; bool ref; }` array + `size_t hand` | `Vec<(FrameId, bool)>` + `usize` |
| `std::find_if(v.begin(), v.end(), [&](auto &e){ return e.id == f; })` | `iter().find(\|(f, _)\| *f == frame)` |
| a reference bit per frame in the buffer descriptor (`BufferDesc.usage_count` in PostgreSQL) | in the frame header, atomically |
| `std::vector<bool>` (a packed bitset with a proxy reference) | `Vec<bool>` is one byte per bool (use `bitvec`/a `u64` for packing) |

### Learn more
- [Clock page replacement](https://en.wikipedia.org/wiki/Page_replacement_algorithm#Clock) · PostgreSQL's [`freelist.c`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/freelist.c) (`StrategyGetBuffer`: the clock sweep) · Linux [`mm/workingset.c`](https://github.com/torvalds/linux/blob/master/mm/workingset.c)

## Part 2 · ClockReplacer::victim: the sweep

**Where this fits.** The hand at work.

### The task

Implement `victim()` in `src/buffer/clock_replacer.rs`: look at the frame under the `hand`. If its reference bit is **set**, clear it and move the hand to the next frame (wrapping to the start); if it is **clear**, remove that frame from the ring and return it, leaving the hand on whatever follows it. An empty ring gives `None`. (A ring whose bits are all set takes one full lap to clear them, then returns the frame the hand started on.)

### Tests

- Frames 1..4 all unpinned: victims 1, 2, 3, 4, then `None`.
- **Second chance:** after victim 1, unpin 2 again: the next victim is **3**, then 4, then 2.
- A new frame joins at the end; a lone frame with its bit set is still evicted; an empty ring is `None`.

### Syntax and methods

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

### Notes

The loop terminates because each lap clears every bit it passes. `remove(hand)` is the neat part: after removal the element that *was* next is at `hand`, so the hand needs no adjustment except wrapping past the end. An `% len` on an empty ring would divide by zero, which is why the empty check comes first.

### In BusTub

(No reference code is given; the sample test is the contract: after the sweep, victims `1, 2, 3` and later `5, 6, 4`, where 4 had its reference bit set by a fresh `Unpin`.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `hand = (hand + 1) % ring.size();` (`% 0` is undefined behaviour in C/C++, a panic in Rust) | `% self.ring.len()` after the empty check |
| `ring.erase(ring.begin() + hand)` shifts elements, invalidating iterators at and after the position | `Vec::remove(hand)`: same shift, and the borrow checker prevents holding a reference across it |
| `while (true) { ... }` with `return` inside | `loop { ... return ... }` (a `loop` can only exit by `return`/`break`, and its type is `!` otherwise) |

### Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · [`loop`](https://doc.rust-lang.org/reference/expressions/loop-expr.html#infinite-loops)
- CMU 15-445 "Memory Management", the slides on CLOCK
