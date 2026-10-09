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

## Finding where the time goes: perf and flamegraphs

A timing tells you *that* something is slow; a **profile** tells you *where*. Build with debug symbols in release mode (`[profile.release] debug = 1`), run a workload long enough to sample (a few seconds), and turn the samples into a **flamegraph**: a stack of boxes where width is the share of samples, so the widest boxes at the top are the hot code.

- **Linux:** `perf record -F 999 -g -- ./target/release/app` then `perf script | inferno-collapse-perf | inferno-flamegraph > flame.svg`, or `cargo flamegraph` (which wraps both).
- **macOS** (no `perf`; `cargo flamegraph` needs `sudo` for dtrace): run the program, then `sample <pid> 5 -file out.txt` and `inferno-collapse-sample out.txt | inferno-flamegraph > flame.svg`. `cargo install inferno` provides the converters.

Read it from the top: a wide `malloc`/`free` band says "allocation", a wide leaf in your own code says "this loop". The workflow is always measure, profile, change one thing, measure again, in release mode: debug timings are not evidence.

## In real code

### Using it: count the work, then time it generously

Time is noisy; **counts are not**. These tests count comparisons and allocations on the current thread, so they are exact and cannot flake, then add one timing guard with a generous limit.

```rust test
use std::cell::Cell;
use std::cmp::Ordering;
use std::collections::BTreeSet;

thread_local! { static COMPARISONS: Cell<u64> = const { Cell::new(0) }; }     // thread-local: parallel tests do not disturb each other

#[derive(PartialEq, Eq, Clone, Copy)]
struct Counted(u64);
impl PartialOrd for Counted { fn partial_cmp(&self, o: &Self) -> Option<Ordering> { Some(self.cmp(o)) } }
impl Ord for Counted {
    fn cmp(&self, o: &Self) -> Ordering { COMPARISONS.with(|c| c.set(c.get() + 1)); self.0.cmp(&o.0) }
}

fn comparisons<R>(f: impl FnOnce() -> R) -> u64 {
    COMPARISONS.with(|c| c.set(0));
    let _ = f();
    COMPARISONS.with(|c| c.get())
}

fn evict_all_by_scan(n: u64) -> u64 {
    comparisons(|| {
        let mut frames: Vec<Counted> = (0..n).map(|i| Counted((i * 7919) % n)).collect();
        while !frames.is_empty() {                                        // the O(n) evict: scan for the minimum, n times
            let mut best = 0;
            for i in 1..frames.len() { if frames[i] < frames[best] { best = i; } }
            frames.swap_remove(best);
        }
    })
}

fn evict_all_by_tree(n: u64) -> u64 {
    comparisons(|| {
        let mut set: BTreeSet<Counted> = (0..n).map(|i| Counted((i * 7919) % n)).collect();
        while set.pop_first().is_some() {}                                // O(log n) each
    })
}

#[test]
fn the_asymptotics_show_up_as_counts_without_any_clock() {
    let (s1, s2) = (evict_all_by_scan(1000), evict_all_by_scan(2000));
    let (t1, t2) = (evict_all_by_tree(1000), evict_all_by_tree(2000));
    assert!(s2 as f64 / s1 as f64 > 3.5, "scan: doubling n should ~quadruple the work ({s1} -> {s2})");
    assert!((t2 as f64 / t1 as f64) < 2.6, "tree: doubling n should ~double the work ({t1} -> {t2})");
    assert!(s2 > 20 * t2, "at n = 2000 the scan already does {}x the comparisons", s2 / t2);
}
```

```rust test
use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;
use std::hint::black_box;
use std::time::{Duration, Instant};

struct CountingAlloc;
thread_local! { static ALLOCS: Cell<usize> = const { Cell::new(0) }; }
unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 { ALLOCS.with(|a| a.set(a.get() + 1)); unsafe { System.alloc(l) } }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) { unsafe { System.dealloc(p, l) } }
}
#[global_allocator]
static A: CountingAlloc = CountingAlloc;

fn allocations<R>(f: impl FnOnce() -> R) -> usize {
    let before = ALLOCS.with(|a| a.get());
    let r = f();
    black_box(r);
    ALLOCS.with(|a| a.get()) - before
}

#[test]
fn count_allocations_to_check_a_no_allocation_claim() {
    let grown = allocations(|| { let mut v = Vec::new(); for i in 0..1000u32 { v.push(i); } v });
    let reserved = allocations(|| { let mut v = Vec::with_capacity(1000); for i in 0..1000u32 { v.push(i); } v });
    assert_eq!(reserved, 1, "with_capacity: one allocation for the whole loop");
    assert!(grown > 5, "push-and-regrow allocates every time the capacity doubles ({grown})");
}

fn median(mut v: Vec<Duration>) -> Duration { v.sort(); v[v.len() / 2] }

#[test]
fn a_timing_guard_with_a_generous_limit_and_a_median() {
    let runs: Vec<Duration> = (0..5).map(|_| {
        let start = Instant::now();
        let mut s = std::collections::BTreeSet::new();
        for i in 0..100_000u64 { s.insert(black_box(i.wrapping_mul(2654435761) % 1_000_003)); }   // black_box: the optimiser may not delete the work
        while s.pop_first().is_some() {}
        start.elapsed()
    }).collect();
    let m = median(runs);
    assert!(m < Duration::from_secs(5), "median {m:?}: something is quadratic, not a slow laptop");   // 100x margin; prints the measurement
}
```

### In the exercises

- **1b-06 (sharded scheduler):** the stage's "Measure it": 200,000 writes over a disk that sleeps per I/O, with 1, 2, 4 and 8 workers, then all to the same page; predict the shape first, then measure.
- **1d-03 and 1e-02:** the 100,000-eviction test and the 400,000-hit test: a time limit with a generous factor is how a quadratic design fails without making the suite slow.
- **1g-02:** a deadlock test under a watchdog timeout: a hang becomes a failed test with a message.
- Every stage's **Performance** section ends with a "Measure it" paragraph; the helpers above are what you paste in.

### Where it is used

- **Benchmark harnesses**: `criterion` and `divan` do warm-up, repetition and outlier analysis; `iai`/`callgrind` count instructions instead of time for exactly the reason in the first test.
- **Profilers**: `perf` and `cargo flamegraph` on Linux, Instruments on macOS, and `heaptrack`/`dhat` for allocations (the counting allocator above is a ten-line version).
- **The Rust Performance Book** and the compiler's own `rustc-perf` suite track instruction counts per commit, since wall time on shared CI machines is too noisy to gate on.
- **Regression gates in CI**: generous time limits for catching accidents, exact counters for catching drift.
