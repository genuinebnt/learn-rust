---
title: Testing with fakes: cargo test, integration tests and in-memory disks
summary: How Rust's test harness maps onto gtest, what a test double buys, and the test patterns this course uses: panics, threads, timeouts and model tests.
minutes: 8
---
The stages here are checked by tests you can read, and the tests only work because the code under them was written against a trait (see the concept on trait objects). This page is how the tests are put together, so you can write your own.

## `cargo test` and gtest

| gtest / CTest | Rust |
|---|---|
| `TEST(Suite, Name) { ... }` | `#[test] fn name() { ... }` |
| `ASSERT_EQ(a, b)` / `EXPECT_EQ` | `assert_eq!(a, b)` (panics: ends the test; there is no "continue after failure") |
| `ASSERT_TRUE(c)` | `assert!(c, "message {x}")` |
| `ASSERT_DEATH(stmt, "regex")` | `#[should_panic(expected = "text")]` |
| `DISABLED_` prefix | `#[ignore]` |
| `ctest -R pattern` / `--gtest_filter` | `cargo test pattern` (a substring of the test's path) |
| show stdout | `cargo test -- --nocapture` |
| one test binary per file | one test binary per file in `tests/` |

A file in `tests/` is an **integration test**: it is compiled as a separate crate that depends on yours, so it can only use your `pub` API. That is the same relationship a user of the library has, which is why BusTub's own tests are ported as `tests/*.rs`. Unit tests (a `#[cfg(test)] mod tests` inside a source file) can reach private items. Tests run **in parallel threads** by default; a test that uses a fixed file name will race with another that does the same.

## Fakes: tests without a disk

A test of the buffer pool should not need a file, a temp directory or cleanup. Because the buffer pool takes a `DiskIo`, the test hands it a fake that keeps the pages in memory:

```rust
let disk = Arc::new(DiskManagerUnlimitedMemory::new());        // implements DiskIo, no file
let bpm = BufferPoolManager::new(10, disk.clone());
```

That gives three things: **speed** (microseconds, so you can run thousands of operations), **determinism** (no timing, no leftover file from a previous run), and **observability** (`disk.get_num_writes()` lets a test assert that eviction wrote exactly one dirty page).

```svg
caption: The trait is the seam. The buffer pool sees a DiskIo either way; production code gives it the file-backed disk, a test gives it an in-memory fake and can ask the fake what happened.
<svg viewBox="0 0 760 210" role="img" aria-label="Two stacks sharing a DiskIo trait: buffer pool over file-backed DiskManager, and buffer pool over an in-memory fake">
<text class="big" x="20" y="24">production</text><text class="big" x="400" y="24">test</text>
<rect class="box" x="20" y="40" width="300" height="38" rx="4"/><text class="mid fg" x="170" y="64">BufferPoolManager</text>
<rect class="box" x="400" y="40" width="340" height="38" rx="4"/><text class="mid fg" x="570" y="64">BufferPoolManager</text>
<rect class="violet" x="20" y="96" width="300" height="30" rx="4"/><text class="mid t-v" x="170" y="116">dyn DiskIo</text>
<rect class="violet" x="400" y="96" width="340" height="30" rx="4"/><text class="mid t-v" x="570" y="116">dyn DiskIo</text>
<rect class="live" x="20" y="146" width="300" height="38" rx="4"/><text class="mid t-g" x="170" y="170">DiskManager: a file on disk</text>
<rect class="hot" x="400" y="146" width="340" height="38" rx="4"/><text class="mid t-a" x="570" y="170">DiskManagerUnlimitedMemory: a Vec</text>
<line class="ln" x1="170" y1="78" x2="170" y2="96"/><line class="ln" x1="170" y1="126" x2="170" y2="146"/>
<line class="ln" x1="570" y1="78" x2="570" y2="96"/><line class="ln" x1="570" y1="126" x2="570" y2="146"/>
<text class="dim sm" x="400" y="204">the test can ask: get_num_writes(), get_memory_usage()</text>
</svg>
```

## Patterns used in this course

- **Panics are part of the contract.** `#[should_panic(expected = "ran out of disk space")]` pins the message, so a *different* panic (an index out of range) does not pass by accident.
- **Threads**: `std::thread::scope(|s| { s.spawn(...); ... })` runs closures that may borrow local variables and joins them before it returns, so a test cannot finish with a thread still running.
- **A deadlock must fail, not hang.** The stage tests wait on results with a timeout and fail with a message when it expires. A test that can hang is worse than one that can fail.
- **Model tests** compare your structure with an obviously correct one (a `HashMap`, a `Vec`) over thousands of pseudo-random operations from a *fixed seed*, so a failure replays exactly. Print the seed and the operation index in the assertion message.
- **Checking an invariant** after each step (`debug_assert!` inside the code, or a `verify_integrity()` called by the test) finds the operation that broke it, not the later one that noticed.

> [!WHY] Why the tests are strict about edges
> The buffer pool above the disk manager assumes a never-written page reads as zeros, that a short read says how short, and that a failed write is not counted. A test that checks only "write then read returns the same bytes" would let all three bugs through, and you would meet them two modules later, far from the cause. The edge tests are there to put the failure next to the code that caused it.
