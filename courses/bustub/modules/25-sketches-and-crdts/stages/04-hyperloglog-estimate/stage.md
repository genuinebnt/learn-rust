The registers hold the evidence; the estimate combines them: `constant × m² / Σ 2^(-register)` over the `m` registers (a harmonic mean, which resists one lucky register), rounded down. A register nobody touched is 0 and contributes `2^0 = 1`.

## The task

In `src/primer/hyperloglog.rs`: `compute_cardinality()` stores `estimate(registers, m)` in the cardinality (`estimate` is the formula, with `CONSTANT = 0.79402`; with no registers the answer is 0). Write the body of `compute_cardinality`: lock the registers, compute, store.

(The formula itself is given as a helper, so this stage is about using it correctly: reading the registers consistently, and the numbers that come out. The tests check what the estimate does.)

## Tests

- An empty sketch with 8 registers estimates `0.79402 × 8`, rounded down: 6.
- With one register, the estimate of nothing is 0 and a value only raises it.
- A negative size has cardinality 0.
- For 100 000 distinct values in a 1 024-register sketch, the estimate is within about +30% (the course's constant runs about 10% high).
- For 2 000 distinct strings in a 256-register sketch the ratio is near 1.

## Syntax and methods

```rust
let registers = self.registers.lock().unwrap();
let value = estimate(registers.iter().map(|r| *r as u32), registers.len());
*self.cardinality.lock().unwrap() = value;
```

## Notes

**Why a harmonic mean.** Averaging the registers' estimates `2^r` arithmetically would let one register with `r = 40` dominate the result. The harmonic mean divides by the sum of `2^-r`: a big `r` adds almost nothing to the sum, so one outlier barely moves the estimate.

**Where the bias comes from.** The constant corrects the systematic over-estimate of the raw formula. This course uses the same constant as BusTub, 0.79402; the usual textbook value for large `m` is `0.7213/(1 + 1.079/m)`, about 10% lower. The tests therefore accept a ratio up to 1.3; the point is the shape of the estimator, not a tuned one.

**Small counts.** For fewer distinct values than registers, many registers are zero; real implementations switch to "linear counting" there. This exercise stops at the basic estimator, as BusTub does.

## In BusTub

`hyperloglog.h`: "`/** @brief Constant for HLL. */ static constexpr double CONSTANT = 0.79402;`" and `ComputeCardinality`. The tests (disabled in the starter, to be enabled by students) derive exact numbers from BusTub's own hash function; this port tests the estimator's behaviour instead.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::pow(2, -r)` | `2f64.powi(-(r as i32))` |
| `static_cast<size_t>(double)` | `x as u64` (truncates toward zero, saturates) |

**Port rule:** `as` between float and integer types saturates in Rust (no undefined behaviour).

## Learn more
- [The HyperLogLog paper](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) · [`f64::powi`](https://doc.rust-lang.org/std/primitive.f64.html#method.powi)

## Performance

`O(m)` per estimate, done when asked, not per insertion: it is the price of cheap inserts. 16 KB of registers are summed in microseconds.

**Measure it.** Call `compute_cardinality` after every insert versus once at the end: the first is `m` times slower overall.

## Hints

### Convert before powering

`r` is a `u8`; `-(r as i32)` avoids unsigned negation.

### Empty registers are 1, not 0

`2^0 = 1` per untouched register: that is why an empty sketch is not 0 (and why the small-count correction exists).
