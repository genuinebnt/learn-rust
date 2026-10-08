CLOCK approximates LRU with one bit per frame and no list update on a hit: frames sit on a ring, a **hand** sweeps over them, and a frame whose bit is set gets a second chance (the bit is cleared and the hand moves on) while the first frame with a clear bit is the victim.

The algorithm is a few lines; the stage is about the **edges**: removing a frame while the hand is pointing past it, wrapping at the end of the ring, and an empty ring. These are the off-by-one bugs of every circular structure.

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

- Frames 1..4 all unpinned: victims 1, 2, 3, 4, then `None`. **Second chance:** after victim 1, unpin 2 again: the next victim is **3**, then 4, then 2.
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

## Part 3 · ClockReplacer::pin: take a frame off the ring

**Where this fits.** Pinning must not disturb where the hand points.

### The task

Implement `pin(frame)` in `src/buffer/clock_replacer.rs`: remove the frame from the ring if it is there. The `hand` must keep pointing at **the same frame it pointed at before** (if the removed frame was *before* the hand, the hand's index shifts down by one; if it was *at* the hand, the hand now points at its successor), wrapping to 0 when it falls off the end. Unknown frames: nothing happens.

### Tests

- A pinned frame leaves the ring and is never a victim; an unknown frame changes nothing.
- The scenario that breaks a careless version: frames 1..6; victim 1; unpin 2 (second chance); victim 3; **pin 2** (it lies behind the hand): the next victims must be 4, then 5. Pinning the frame under the hand moves on to its successor; pinning the last frame wraps.

### Syntax and methods

```rust
let Some(at) = self.ring.iter().position(|(f, _)| *f == frame) else { return };   // Iterator::position -> Option<usize>
self.ring.remove(at);
if at < self.hand { self.hand -= 1; }
if self.hand >= self.ring.len() { self.hand = 0; }
```

### Notes

This is an **index invalidation** bug waiting to happen, in any language: you store a position, then remove something before it. In C++ the analogue is an iterator or index kept across `erase`. Rust's borrow checker can't help with a plain `usize`; tests do. (If the hand were a reference into the `Vec`, the borrow checker *would* stop you from removing anything while it is held, which is the reason to keep it an index.)

### In BusTub

```cpp
// The sample test: Pin(3) (already victimised, a no-op), Pin(4) (removes it), then Unpin(4) sets the reference bit again.
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = std::find(...); ring.erase(it);` with an index `hand` kept elsewhere: the classic stale-index bug | `position` + `remove` + explicit fix-up of `hand` |
| `std::vector::erase` invalidates iterators/pointers/references at or after the erased element | the same data movement; `&`/`&mut` into the `Vec` can't outlive the call |
| `std::deque`, `std::list` give stable iterators across erases of *other* elements | an arena (stage 1) gives stable handles; a `Vec` ring does not |

**Port rule:** every stored index into a `Vec` is a promise that nothing before it is removed. Either use handles (generational) or fix the index up at every removal, and test it.

### Learn more
- [`Iterator::position`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position) · [`Vec::retain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.retain)

## Performance

A hit costs **one bit set** (no list write), which is the whole reason operating systems use CLOCK. `victim` is O(n) in the worst case: if every bit is set, the hand makes a full revolution clearing them, then takes the first. Amortised over a workload it is much cheaper: each revolution clears bits that were set by *accesses*, so the sweep work is bounded by the number of accesses since the last sweep. `pin` is O(n) here because the ring is a `Vec` searched for the frame (an index map would make it O(1) at the cost of keeping the map in step with every removal shift).

CLOCK is an *approximation*: it can evict a frame LRU would keep, because a single bit cannot tell "used a microsecond ago" from "used almost a revolution ago".

**Measure it.** Replay a Zipf-distributed access trace (a few hot pages, a long tail) through your LRU and your CLOCK with a cache of 10% of the pages and compare hit ratios (CLOCK is usually within a few points), and time 1 000 000 accesses in each to see the difference in cost per hit.

## Hints

### Where is the hand after a removal?

The hand is an **index into the ring**; removing an element at position `at` shifts everything after it left by one. If `at < hand` the hand must decrement or it will now skip a frame; if `at == hand` the hand already points at the next frame (the one that slid into place); and if the removal was the last element the hand must wrap to 0. Write those three cases as a small table before coding, then test each one separately: this is where CLOCK implementations go wrong.

### Why does the sweep terminate?

Each pass of the hand over a frame with its bit set **clears** that bit. After at most one full revolution every bit is clear, so the next frame is chosen. State that argument in a comment: it is the termination proof, and it tells you the sweep needs no iteration counter. Also decide what `victim` returns for an empty ring (`None`) *before* entering the loop: a loop over an empty ring never finds a clear bit.

### A new frame arrives with its bit set: why?

`unpin` means "this frame was just used", so it enters with its reference bit **set**: it deserves at least one full revolution before it can be chosen. A frame added with a clear bit would be the very next victim, which turns CLOCK into FIFO for fresh frames. And `unpin` of a frame already on the ring should only set the bit, never add a second copy.
