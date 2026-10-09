**Where this fits.** The last stage of the module: BusTub's own tests for what you built.

## The task

Nothing new to write. Run BusTub's two tests, ported in `tests/`:

| BusTub | here | checks |
|---|---|---|
| `DiskSchedulerTest.ScheduleWriteReadPageTest` | `schedule_write_read_page_test` | write page 0 then read it, both through the scheduler; the page read equals the page written |
| `RWLatchTest.BasicTest` | `basic_test` | 100 threads, 50 readers and 50 writers adding 1; the total is 55 |

The C++ test passes `char *` buffers; the port gives each request an owned `Box<PageData>` and takes the buffer back from the future (stage 7). Everything else is line for line.

## Tests

- `s1b_15_*`: the module works as a whole (below). Plus the two BusTub tests.

## Syntax and methods

```rust
let (promise1, future1) = disk_scheduler.create_promise();
let r1 = DiskRequest { is_write: true, data, page_id: PageId(0), callback: promise1 };
disk_scheduler.schedule(vec![r1]);
future1.get().unwrap().unwrap()      // outer unwrap: the promise wasn't broken; inner: the I/O succeeded
```

## Notes

If `schedule_write_read_page_test` hangs, a promise is never completed: look at `execute` and at your `Drop`. If `basic_test` sometimes fails, a latch is letting a writer in beside another holder.

## In BusTub

```cpp
auto promise1 = disk_scheduler->CreatePromise();
auto future1 = promise1.get_future();
DiskRequest r1{/*is_write=*/true, data, /*page_id=*/0, std::move(promise1)};
std::vector<DiskRequest> requests1;  requests1.push_back(std::move(r1));
disk_scheduler->Schedule(requests1);
...
ASSERT_TRUE(future1.get());   ASSERT_TRUE(future2.get());
disk_scheduler = nullptr;     // Call the DiskScheduler destructor to finish all scheduled jobs.
```

## The C/C++ way

| gtest / C++ | Rust test |
|---|---|
| `ASSERT_TRUE(future1.get())` | `assert!(future1.get().unwrap().is_ok())` |
| `disk_scheduler = nullptr;` runs the destructor (a `unique_ptr`) | `drop(disk_scheduler)` |
| `std::vector<std::thread> threads; ... threads[i].join();` | `Vec<JoinHandle<()>>` and `.join().unwrap()` |
| `ReaderWriterLatch mutex_` next to `int count_` | `ReaderWriterLatch<i32>` owning the count |
| `memcmp(buf, data, sizeof(buf))` | `*buf == *data` (arrays compare by value) |

## Experiment

Optional. Predict first, write the prediction down, then run it.

1. **A scheduler that forgets to wait.** Take the `join` out of `Drop for DiskScheduler`. Which of the two tests can still pass? Could either hang, or panic at the end of the process? What does that say about why the stop signal and the join are both needed?
2. **A slow disk.** Make `execute` sleep 50 ms before each request and schedule 100 writes through the single worker. Predict the total time, then measure it. What would the sharded scheduler of stage 4 change, and for which page ids would it change nothing?

## What you built

A blocking queue, a one-shot promise/future, a worker thread that runs disk requests in order and shuts down cleanly even if the disk panics, a reader-writer latch, and a sharded scheduler. Next module: **replacers**, the eviction policies (LRU, CLOCK, LRU-K, ARC) the buffer pool uses to choose which page to drop.

## Learn more
- BusTub's [disk_scheduler_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/storage/disk_scheduler_test.cpp) and [rwlatch_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/common/rwlatch_test.cpp) · the [Project 1 page](https://15445.courses.cs.cmu.edu/fall2026/project1/)
