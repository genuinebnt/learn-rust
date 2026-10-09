A challenge: no walkthrough, no hints, no solution. Solve it with what the five stages before it taught. It is extra practice and does not count towards the course.

## What to build

Variable-length integers in `src/rust_primer/varint.rs`: `encode_varint` writes a `u64` using as few bytes as it needs, and `decode_varint` reads one back, saying how many bytes it took.

The format: the number is cut into groups of 7 bits, lowest group first. Each group is one byte; the high bit of a byte is set when another byte follows. So 0 to 127 take one byte, 128 takes two, and `u64::MAX` takes ten.

## Why

Databases and network protocols are full of small numbers that are sometimes huge: lengths, offsets, counts. A fixed 8 bytes for each wastes space; a varint spends one byte on most of them. The log in module 4c and the pages you will meet later would be smaller with it. It is also a compact exercise in reading a format from a description and being strict about bad input.

## The contract

- `encode_varint(v, out)` appends to `out`, always in the fewest bytes.
- `decode_varint(bytes)` returns `(value, bytes_used)` and ignores whatever follows the number.
- Bytes that are not one varint are an error, never a panic: `Truncated` (the bytes end mid-number), `Overflow` (the number does not fit in 64 bits), `NonMinimal` (right number, but written with more bytes than needed, like `0` as `[0x80, 0x00]`).

## What the tests check

- The exact bytes of a handful of numbers, including the edges 0, 127, 128 and `u64::MAX`.
- A property over random numbers: they round-trip, in the fewest bytes, with trailing bytes untouched.
- A property over streams of numbers, including streams cut in the middle of a number.
- A property over random bytes: decoding never panics, and anything it accepts re-encodes to exactly the bytes it read.

## Done when

All the `sr_c1` tests pass.
