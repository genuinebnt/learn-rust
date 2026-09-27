A proxy submits reads and writes through an io_uring-style submission ring: an array of `Sqe` entries
in shared memory that a C consumer reads by field offset. `Sqe` stays `#[repr(C)]` (the C header is
generated from it), and the consumer reads the first byte, `opcode`, before anything else.

1. **Quiz.** Fill in `LAYOUT`: the `(size, align)` of the types `Q1` to `Q8`, in order. Reason it out:
   `size_of`, `align_of`, `offset_of!` and `Layout` are off limits in your code.
2. **Shrink.** `Sqe` is 72 bytes, 24 of them padding. Reorder its fields so it is **48 bytes with no
   padding**, align 8, still `#[repr(C)]`, with `opcode` at offset 0. Keep every field and its type.
3. **Ring.** Finish `SqRing`: `entries` slots (a power of two) and free-running `u32` `head` and `tail`
   counters, as the kernel keeps them. An entry lives in slot `counter & mask`; the counters wrap at
   `u32::MAX`, and the length is their wrapping difference. `push` hands the entry back when the ring
   is full; `pop` takes the oldest. `starting_at(entries, counter)` starts both counters at `counter`.
