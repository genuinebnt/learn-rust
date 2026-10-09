Presto's HyperLogLog stores each register compactly. The run length is the number of **trailing** zeros of the bits after the register bits (the whole remainder zero gives all `64 - b` of them). It is split in two: the low 4 bits go in a **dense** array (one small value per register), and the next 3 bits go in a sparse **overflow** map that has an entry only for registers whose run is 16 or more.

## The task

In `src/primer/hyperloglog.rs`, `HyperLogLogPresto` (the hash is given: integers hash to themselves, so a test can choose the bits):

- `add_elem(&val)`: with no registers do nothing; the register is the top `n_leading_bits` bits of the hash (0 if there are none); the run is the trailing zeros of the other `64 - b` bits (all of them if the rest is zero); if the run exceeds the register's current value (`register(idx)`, given: dense bits plus overflow bits shifted left by 4) store `run & 0xF` in the dense array and `(run >> 4) & 0x7` in the overflow map (removing the entry if it is zero).
- `compute_cardinality()`: the same estimate as HyperLogLog, over the registers reassembled from dense and overflow bits.

## Tests

- 2^18 (register 0, 18 trailing zeros): dense 2, overflow 1; estimate 3.
- Adding 0 gives all 63 remaining bits: dense 15, overflow 3.
- A third value in register 1 with 56 trailing zeros: dense 8, and the estimate is exactly 227086569448168320.
- A value with no trailing zeros changes nothing; `i64::MIN` and 0 with one register bit (and with none) give BusTub's numbers.
- A negative size has cardinality 0; strings estimate about half the true number (see Notes).

## Syntax and methods

```rust
let idx = if b == 0 { 0 } else { (hash >> (64 - b)) as usize };
let rest_bits = 64 - b;
let tz = (hash & ((1u64 << rest_bits) - 1)).trailing_zeros().min(rest_bits);   // rest_bits < 64
self.dense.lock().unwrap()[idx] = (tz & 0xF) as u8;
```

## Notes

**Where the numbers come from.** With `b = 1` and value `-9151314442816847872` = 2^63 + 2^56: the top bit is 1 (register 1) and bit 56 is the lowest set bit of the rest, so the run is 56: `56 = 0b11_1000`, dense `8`, overflow `3`. The estimate is `0.79402 × 4 / (2^-63 + 2^-56)`, which is 227 086 569 448 168 320 as a `u64`. Every such expected value in the tests follows from this definition; use them to check your reading of "trailing zeros".

**Half the estimate.** The run here is the *number* of trailing zeros, one less than the *position* of the first 1 that plain HyperLogLog counts. Every register's `2^-r` term is therefore twice as large, and the estimate about half as large. That is a property of the specified design, kept so that BusTub's exact values hold; the string test accepts ratios between 0.35 and 0.8.

**Why split.** Runs rarely reach 16; most registers need 4 bits, and only the rare big one needs its overflow bits. A dense array of 4-bit values plus a small map saves memory over 7 bits for every register.

## In BusTub

`hyperloglog_presto.h`: "`DENSE_BUCKET_SIZE = 4`, `OVERFLOW_BUCKET_SIZE = 3`", "`Testing framework will use the GetDenseBucket and GetOverflow function, hence SHOULD NOT be deleted. It's essential to use the dense_bucket_ data structure.`" and the tests `PrestoCase1`, `PrestoCase2`, `PrestoEdgeCase` whose expected values appear above.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<std::bitset<4>>` and `std::bitset<3>` | `Vec<u8>` (0 to 15) and `u8` (0 to 7) |
| `bitset.to_ullong()` | the integer itself |
| `std::unordered_map<uint16_t, std::bitset<3>>` | `HashMap<u16, u8>` |

**Port rule:** small bitsets are small integers; the mask and shift are explicit.

## Learn more
- [Presto's HyperLogLog](https://engineering.fb.com/2018/12/13/data-infrastructure/hyperloglog/) · [`u64::trailing_zeros`](https://doc.rust-lang.org/std/primitive.u64.html#method.trailing_zeros)

## Performance

Dense storage is `m × 4 bits`; overflow entries exist only for registers with runs of 16 or more (probability about `2^-16` per hash), so for typical data the map is empty. The estimate sums over `m` registers rebuilt from two arrays: `O(m)`.

**Measure it.** Count overflow entries after adding a million values with `b = 12`: a handful.

## Hints

### Mask before counting

Counting trailing zeros of the whole hash would include the register bits when the remainder is zero. Mask to `64 - b` bits first and cap at that.

### The all-zero remainder is 64 - b, not 64

`trailing_zeros` of 0 is 64; with `b = 1` the expected run is 63.

### Remove empty overflow entries

If the new run is 15 or less after having been 16 or more... it cannot be (runs only grow). But storing a run below 16 must not leave a stale overflow value from before.
