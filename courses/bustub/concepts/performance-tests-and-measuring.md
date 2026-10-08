---
title: Measuring performance: timing tests, release profiles and what to trust
summary: How to test that something is fast enough without a flaky test, why debug builds lie, and how to read a measurement: the habits behind every Performance section in this course.
minutes: 9
---
Each stage here has a **Performance** section and some have a timing assertion (ARC's runs a quarter of a million accesses and must finish in a few seconds). Performance tests are the flakiest tests there are, and most performance advice is wrong because it was never measured. This is how to do it properly.

## Debug builds are not representative

`cargo test` builds with the `test` profile, which in this repo sets `opt-level = 1` (see `Cargo.toml`), so tests are fast enough to be useful. A plain debug build is typically many times slower than release, and the slowdown is **uneven**: iterator chains, bounds checks and overflow checks cost far more unoptimised. Rules:

- never conclude "this is slow" from a debug run, and never conclude "this is fast enough" from one;
- when a number matters, run `cargo test --release` (or a `--release` benchmark) and compare like with like;
- the timing assertions in the stage tests use *generous* limits (seconds, not microseconds) so that they catch an accidentally quadratic algorithm and not a slow laptop.

## Asymptotics first, constants second

A hundred-thousand-frame test separates O(n) from O(log n) by a factor you can see on any machine: 10<sup>5</sup> evictions each scanning 10<sup>5</sup> frames is 10<sup>10</sup> operations (tens of seconds), against about 1.7 million for the tree (milliseconds). That gap is the test. It cannot be flaky because it is not close.

| claim | how to check it |
|---|---|
| O(1) versus O(n) | time at n and 10n: the first stays flat, the second grows tenfold |
| O(log n) versus O(n) | time at n = 10<sup>3</sup>, 10<sup>4</sup>, 10<sup>5</sup> |
| "no allocation in the hot path" | count them (a counting allocator, or `heaptrack`/`valgrind --tool=dhat`) |
| "one syscall per call" | `strace -c` (Linux) or `dtruss -c` (macOS, needs privileges) |
| "no lock contention" | per-thread timers, or `perf`/Instruments |

## Writing a timing test that does not flake

```rust
let start = Instant::now();
for i in 0..n { /* the work */ }
assert!(start.elapsed() < Duration::from_secs(5), "took {:?}: something is not O(log n)", start.elapsed());
```

- A **generous limit**, justified by a margin of 10x or more over the expected time on a slow machine.
- A **message that prints the measurement**, so a failure is diagnosable from the log.
- **Warm up** if a one-off cost (first allocation, page faults, a cold cache) would distort a small run, and **repeat** and take the minimum or median if you compare two versions.
- `std::hint::black_box(x)` stops the optimiser deleting work whose result is unused: without it a loop that "does nothing" runs in zero time in release.
- Tests run **in parallel**; two timing tests on one CPU slow each other. Run a single one with `cargo test name -- --test-threads=1`.

## Reading a measurement

Prefer the **minimum** of several runs when you want to know what the code *can* do (noise only adds time), the **median** for what it usually does, and a **percentile** (p99) for what a user occasionally sees. A mean hides the tail; a single run proves nothing. For anything finer than a regression guard use a benchmark harness (`criterion`, or the unstable `#[bench]`), which handles warm-up, outliers and statistics.

## Cost models: the habit this course asks for

Before measuring, **predict**. For a stage's code, write down: how many system calls per operation, how many allocations, how long each lock is held, how many cache lines are touched. Then measure and reconcile. If the prediction was wrong, you learned something about the machine or the code; if you never predicted, you only learned a number.

> [!TIP] A cheap profiler
> `cargo build --release` then `perf record -g ./target/release/...` and `perf report` (Linux), or Instruments' Time Profiler (macOS), shows where the time goes in minutes. Look for the *one* function that dominates before optimising anything.
