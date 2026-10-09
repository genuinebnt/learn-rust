HyperLogLog hashes every item to 64 bits and uses the bits twice: the first `b` bits choose one of `2^b` **registers**; in the remaining bits, the **position of the leftmost 1** (the run of zeros before it, plus one) is how rare the hash is. Each register keeps the largest rank it has seen.

## The task

In `src/primer/hyperloglog.rs` (`hash64` is given: a 64-bit hash with well-mixed bits):

- `register_index(hash)`: the top `n_bits` bits of the hash as a number; 0 when `n_bits` is 0.
- `position_of_leftmost_one(hash)`: drop the first `n_bits` bits (shift left), count the leading zeros of what is left (at most `64 - n_bits`), plus one. An all-zero rest gives `64 - n_bits + 1`.
- `add_elem(&val)`: hash it; with no registers (negative `n_bits`) do nothing; otherwise raise the register at `register_index` to `position_of_leftmost_one` if that is larger (under the lock).

## Tests

- The register is the top bits (0 for no register bits).
- The rank is the position of the leftmost 1 after the register bits, including the all-zero case and the last bit; with zero register bits all 64 bits count.
- Adding a value raises exactly one register; adding it again changes nothing; registers only ever grow.
- A negative size has no registers. Adding from eight threads gives the registers a sequential run gives (`registers()` is given for the tests).

## Syntax and methods

```rust
(hash >> (64 - self.n_bits as u32)) as usize           // careful: a shift by 64 is an overflow
let rest = hash << used;                                // drop the register bits
(rest.leading_zeros().min(64 - used) + 1) as u8
```

## Notes

**The edge shifts.** `hash >> 64` and `hash << 64` overflow for a `u64`; handle `n_bits == 0` for the first and `used >= 64` for the second explicitly.

**The `min` matters.** After shifting out `used` bits, the low `used` bits of `rest` are zeros that were not in the hash. An all-zero `rest` has 64 leading zeros, but only `64 - used` of them are real; the cap gives the "all zeros" rank.

**Registers store the maximum.** A smaller rank never lowers a register; that is also why two sketches merge by taking element-wise maxima.

## In BusTub

`hyperloglog.h`: "`Calculates Hash of a given value.`", `ComputeBinary(hash) -> std::bitset<64>`, `PositionOfLeftmostOne(bset)` ("`Function that computes leading zeros.`") and `AddElem`. The BusTub version builds a `bitset`; with a `u64` the same work is `leading_zeros`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::bitset<64>` built from the hash, scanned bit by bit | `u64::leading_zeros()` |
| `std::mutex` guarding `registers_` | `Mutex<Vec<u8>>` |

**Port rule:** bit-by-bit loops over a `bitset` are `leading_zeros`, `trailing_zeros` and shifts on an integer.

## Learn more
- [`u64::leading_zeros`](https://doc.rust-lang.org/std/primitive.u64.html#method.leading_zeros) · [HyperLogLog (Wikipedia)](https://en.wikipedia.org/wiki/HyperLogLog)

## Performance

`add_elem` is a hash, two shifts, one `leading_zeros` instruction and a compare under a lock: tens of nanoseconds. The sketch's size is `2^b` bytes however many items are added.

**Measure it.** Add 10 million values to a `b = 14` sketch: 16 KB, a second or less.

## Hints

### Test the edges first

`register_index(u64::MAX)` for `b = 3` is 7; `position_of_leftmost_one(1 << 63)` for `b = 0` is 1.

### Compare as numbers

Registers are `u8`; the rank can be up to 65. Do not accidentally truncate.
