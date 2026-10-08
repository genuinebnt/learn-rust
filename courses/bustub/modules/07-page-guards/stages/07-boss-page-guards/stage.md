**Where this fits.** The end of Project 1: BusTub's own tests for the buffer pool and its page guards.

## The task

Nothing new, if the earlier stages are right. Run the ported tests:

| BusTub | here | checks |
|---|---|---|
| `BufferPoolManagerTest.VeryBasicTest` | `very_basic_test` | write, then read twice, then delete |
| `PagePinEasyTest` | `page_pin_easy_test` | a 2-frame pool: pinned pages block new ones; unpinning makes room; evicted pages come back from disk with their updates |
| `PagePinMediumTest` | `page_pin_medium_test` | a 10-frame pool: fill it, unpin half, new pages evict the oldest, page 0 is still readable |
| `PageAccessTest` | `page_access_test` | one frame, a writer thread and a reader thread: while a reader holds the page, nobody modifies it |
| `ContentionTest` | `contention_test` | 4 threads × 100,000 write guards on one page |
| `DeadlockTest` | `deadlock_test` | the scenario of stage 6 |
| `EvictableTest` | `evictable_test` | 1000 rounds, 8 readers, one frame: the frame is never evictable while any reader holds it |
| `PageGuardTest.DropTest` | `page_guard_test::drop_test` | drops unpin, double drops are harmless, latches are released |
| `PageGuardTest.MoveTest` | `page_guard_test::move_test` | moving and reassigning guards keeps pin counts right |

## Tests

- `s1g_07_*`: guards moved into a `Vec` keep their pages pinned; assigning a guard drops the one it replaces; four threads incrementing one page 500 times each lose nothing.
- The nine BusTub tests above.

## Syntax and methods

```rust
thread::scope(|scope| {                       // scoped threads can borrow the pool: no Arc needed
    scope.spawn(|| { let guard = bpm.write_page(pid); /* .. */ });
});                                           // all spawned threads are joined here
```

## Notes

**What the C++ move test checks and Rust doesn't need to.** C++ moves leave a hollow object behind, so `MoveTest` checks that the hollow guard's destructor does nothing, and that moving a guard onto itself is harmless. In Rust a moved-from guard is gone and self-assignment doesn't compile: two of the C++ test's cases vanish, and the rest become `guard0 = guard1;` (assignment drops the old value, unpinning it).

**If a test hangs:** a latch or a pin wasn't released. Run the failing test alone with `-- --nocapture --test-threads=1`, add `eprintln!` in `release()`, and look at which page's pin count never returns to 0.

## In BusTub

```cpp
auto guard0 = bpm->ReadPage(pid0);  auto guard1 = bpm->ReadPage(pid1);
guard0 = std::move(guard1);                       // "Invalidate the old guard0 by move assignment."
ASSERT_EQ(0, bpm->GetPinCount(pid0));  ASSERT_EQ(1, bpm->GetPinCount(pid1));
```

## The C/C++ way

| gtest / C++ | Rust |
|---|---|
| `std::thread t([&]{ ... }); t.join();` capturing by reference | `thread::scope(\|s\| { s.spawn(\|\| ...); })` |
| `std::vector<WritePageGuard>` + `push_back(std::move(g))`, `erase(begin())` | `Vec<WritePageGuard>`, `push(g)`, `remove(0)` |
| `std::atomic<bool> start; while (!start.load()) {}` busy-wait | `AtomicBool` with `load(SeqCst)`; real code would use a channel or `Condvar` |
| `EXPECT_STREQ(guard.GetData(), str.c_str())` | compare the bytes up to the first NUL |
| `ASSERT_EQ(1, bpm->GetPinCount(pid0))` against an `optional<size_t>` | `assert_eq!(Some(1), bpm.get_pin_count(pid0))` |

## What you built

**BusTub Project 1, complete:** a disk manager, a scheduler with a worker thread, four replacement policies, a buffer pool, and RAII page guards, with every part tested against BusTub's own tests. Everything above this line is a storage engine's foundation. Next: **Project 2, the indexes** (typed pages, extendible hashing, the B+ tree), which live entirely inside pages obtained from this pool.

## Learn more
- BusTub's [buffer_pool_manager_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/buffer/buffer_pool_manager_test.cpp) · the [Project 1 page](https://15445.courses.cs.cmu.edu/fall2026/project1/) · [`thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html)
