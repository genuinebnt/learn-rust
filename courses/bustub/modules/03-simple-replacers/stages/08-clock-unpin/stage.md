**Where this fits.** LRU needs a list update on every access. **CLOCK** approximates LRU with one bit per frame and a sweeping hand: much cheaper, and what PostgreSQL and the Linux kernel's page cache use.

## The task

`ClockReplacer` (`src/buffer/clock_replacer.rs`) keeps a ring of `(FrameId, bool)` (the bool is the **reference bit**) and a `hand`. Implement:
- `unpin(frame)`: a frame already on the ring gets its reference bit set; a new frame is added at the **end** of the ring with its bit set. If the ring already has `capacity` frames, panic with "full";
- `size()`: how many frames are on the ring.

## Tests

- 6 unpins give size 6; unpinning twice counts once; a 2nd frame on a 1-frame replacer panics ("full").

## Syntax and methods

```rust
match self.ring.iter_mut().find(|(f, _)| *f == frame) {     // iter_mut + find: a mutable reference to the slot, if any
    Some(slot) => slot.1 = true,                              // tuple fields: .0 and .1
    None => self.ring.push((frame, true)),
}
```

## Notes

**Why CLOCK.** On a page hit, LRU must move the page in a shared list: a lock and several writes. CLOCK only sets a bit. The hand does the work later, on eviction: it gives a frame with its bit set "a second chance" by clearing the bit; the first frame whose bit is already clear is the victim. The ring can be a plain `Vec` because the hand moves forward only; searching for a frame is `O(n)` here, which is fine for the sweep and the reason real implementations store the bit inside the frame's own header.

## In BusTub

```cpp
class ClockReplacer : public Replacer { /* TODO(student): implement me! */ };
```

(BusTub gives no implementation and a single sample test; the textbook algorithm is what is expected.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `struct { frame_id_t id; bool ref; }` array + `size_t hand` | `Vec<(FrameId, bool)>` + `usize` |
| `std::find_if(v.begin(), v.end(), [&](auto &e){ return e.id == f; })` | `iter().find(\|(f, _)\| *f == frame)` |
| a reference bit per frame in the buffer descriptor (`BufferDesc.usage_count` in PostgreSQL) | in the frame header, atomically |
| `std::vector<bool>` (a packed bitset with a proxy reference) | `Vec<bool>` is one byte per bool (use `bitvec`/a `u64` for packing) |

## Learn more
- [Clock page replacement](https://en.wikipedia.org/wiki/Page_replacement_algorithm#Clock) · PostgreSQL's [`freelist.c`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/freelist.c) (`StrategyGetBuffer`: the clock sweep) · Linux [`mm/workingset.c`](https://github.com/torvalds/linux/blob/master/mm/workingset.c)
