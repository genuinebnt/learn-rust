**Where this fits.** The last piece, and then BusTub's own test for the disk manager.

## The task

Implement `shut_down` in `src/storage/disk/disk_manager.rs`: make sure what was written has reached the device, for both the db file and the log.

Then run BusTub's own test, ported test for test in `tests/disk_manager_test.rs`:

| BusTub (`disk_manager_test.cpp`) | here | checks |
|---|---|---|
| `ReadWritePageTest` | `read_write_page_test` | pages 0 and 5 round-trip, after an empty read |
| `ReadWriteLogTest` | `read_write_log_test` | a log record round-trips |
| `DeletePageTest` | `delete_page_test` | 100 pages written, then 200 written and deleted: **the file must not grow** |
| `ThrowBadFileTest` | `throw_bad_file_test` | a bad path is an error (an `Exception` in C++, an `Err` here) |

Every one should already pass with what you built. If `delete_page_test` fails, look at the free list and the file size.

## Tests

- `shut_down` succeeds, the page and the log record are still there afterwards, and calling it twice is fine.
- The four BusTub tests above.

## Syntax and methods

```rust
self.db_io.lock().unwrap().file.sync_all()?;   // io::Result<()>
```

## Notes

Writing to a file hands bytes to the operating system, which keeps them in its page cache and writes them out later. `File::sync_all` asks the OS to push the file's data **and** metadata to the device and wait (`fsync`); `sync_data` skips metadata not needed to read the data back. BusTub's `ShutDown()` only *closes* the streams and never `fsync`s: a flush in C++ pushes to the OS, not to the disk. The gap between "written" and "durable" is what the Recovery module is about.

## In BusTub

```cpp
void DiskManager::ShutDown() {
  { std::scoped_lock scoped_db_io_latch(db_io_latch_); db_io_.close(); }
  log_io_.close();
}
```

## What you built

BusTub Project 1's disk manager: page-sized I/O at slot offsets, a page table, a free list, doubling growth, a log file, and three interchangeable disks behind one trait. Next: the **disk scheduler**, a background thread that runs these calls for the buffer pool.

## The C/C++ way
| C / C++ (gtest) | Rust |
|---|---|
| `EXPECT_EQ(a, b)` (continues on failure), `ASSERT_EQ(a, b)` (stops) | `assert_eq!(a, b)` (always stops this test; tests are independent) |
| `EXPECT_EQ(std::memcmp(buf, data, sizeof(buf)), 0)` | `assert!(buf == data)` (arrays compare by value) |
| `EXPECT_THROW(DiskManager("bad/path"), Exception)` | `assert!(DiskManager::new("bad/path").is_err())`, or `#[should_panic]` for panics |
| `TEST_F(Fixture, Name)` with `SetUp`/`TearDown` removing `test.bustub` | a `TempDir` guard whose `Drop` cleans up (each test gets its own directory, so tests run in parallel) |
| `DISABLED_` prefix to skip a test | `#[ignore]` |
| `fsync(fd)` | `file.sync_all()` |
| `db_io_.close()` in `ShutDown()`, and the destructor closes too | `Drop` closes; `shut_down` only adds the `sync_all` BusTub doesn't do |

**Port rule:** tests that share fixed file names (`test.bustub`) in C++ run one at a time; in Rust they run on parallel threads, so each test needs its own directory.

## Learn more
- [`File::sync_all`](https://doc.rust-lang.org/std/fs/struct.File.html#method.sync_all) · [`sync_data`](https://doc.rust-lang.org/std/fs/struct.File.html#method.sync_data)
- CMU 15-445 lecture "Database Storage I" (in the module resources below) and the [Project 1 page](https://15445.courses.cs.cmu.edu/fall2026/project1/)
