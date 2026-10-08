Observability and the log. The counters the tests and benchmarks read, `write_log` (an append-only file, one atomic append per call) and `read_log` (read from an offset, with a clean end-of-log signal). The code is short; the content is the contracts: count only what succeeded, never trust a log buffer's length, and do not call an empty write a flush.

> [!TIP] Watch the syscalls
> `strace -f -e trace=pwrite64,write,pread64 cargo test s1a_ …` (Linux) shows what each call really does: positional writes carry their offset, and the log's `write` carries no offset at all because `O_APPEND` chooses it. On macOS use `sudo fs_usage -w -f filesys <pid>`.

## Part 1 · Count the I/O with atomics

**Where this fits.** Later modules assert how many writes happened ("the buffer pool wrote the dirty page exactly once"). The disk manager keeps the count.

### The task

Three counters (`num_writes`, `num_deletes`, `num_flushes`) live outside the mutex as `AtomicUsize`. In `src/storage/disk/disk_manager.rs`:
- count a write in `write_page` (every call, rewrites included) and a delete in `delete_page` (only when the page existed);
- fill in the getters `get_num_writes`, `get_num_deletes`, `get_num_flushes`. (Flushes are counted by the log, stage 14.)

### Tests

- The three counters count only what succeeded: of three `delete_page` calls (one real, one repeat, one unknown) one counts; eight threads writing 50 pages each make exactly 400.

### Syntax and methods

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let n = AtomicUsize::new(0);          // not `mut`: atomics change through &self
n.fetch_add(1, Ordering::Relaxed);    // one indivisible increment; returns the old value
n.load(Ordering::Relaxed)             // the current value
```

### Notes

Why not put the counters in `DbIo`? So that anyone can read them without the file lock, and so incrementing from many threads can never race. `Ordering::Relaxed` means "this number must be right, but I don't need it to order any other memory": exactly right for a statistic. (`Acquire`/`Release` come later, in the lock-free structures.)

### In BusTub

```cpp
num_writes_ += 1;                                           // a plain int, bumped under db_io_latch_
auto DiskManager::GetNumWrites() const -> int { return num_writes_; }   // read with no lock: a data race
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `int num_writes_; num_writes_ += 1;` from many threads: a **data race, undefined behaviour** | `AtomicUsize::fetch_add`, or increment under the mutex |
| `std::atomic<int> n; n.fetch_add(1);` defaults to `memory_order_seq_cst` (the strongest, slowest) | the ordering is always spelled out: `Ordering::Relaxed` for a statistic |
| C11 `<stdatomic.h>`: `atomic_fetch_add_explicit(&n, 1, memory_order_relaxed)` | same operation, same ordering names |
| `memory_order_relaxed / acquire / release / acq_rel / seq_cst` | `Ordering::Relaxed / Acquire / Release / AcqRel / SeqCst` (no `consume`) |
| a getter that reads a plain int without the lock (BusTub's `GetNumWrites`) | `load(Relaxed)`: a defined, race-free read |

**Port rule:** every shared counter that C++ wrote as a plain `int` and "protected by convention" is either `Atomic*` or inside the `Mutex`. Pick `Relaxed` only when the number does not order other memory.

### Learn more
- [`AtomicUsize`](https://doc.rust-lang.org/std/sync/atomic/type.AtomicUsize.html) · [`Ordering`](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)

## Part 2 · write_log: append to the log file

**Where this fits.** The disk manager has a second file: the **write-ahead log** (the Recovery module builds the real one). For now it is a byte stream you can append to.

### The task

Implement `write_log(data)` in `src/storage/disk/disk_manager.rs`: append `data` to the log file and count one flush; an empty `data` does nothing at all.

### Tests

- `write_log` appends (`abc` then `def` leaves `abcdef`), counts one flush per non-empty write, and keeps old records after reopening.

### Syntax and methods

```rust
use std::io::Write;
let mut log = self.log_io.lock().unwrap();   // `mut`: Write::write_all takes &mut self
log.write_all(data)?;                        // io::Result<()>
```

### Notes

The file was opened with `append(true)`, so each `write_all` lands at the end regardless of anything else. Appending is also the fastest way to write to a disk, which is why logs are append-only.

### In BusTub

```cpp
void DiskManager::WriteLog(char *log_data, int size) {
  if (size == 0) { return; }   // no effect on num_flushes_ if log buffer is empty
  num_flushes_ += 1;
  log_io_.write(log_data, size);   // sequence write
  log_io_.flush();                 // flushes the *stream's* buffer to the OS; not an fsync
}
```

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `open(.., O_WRONLY \| O_APPEND)`; `write(fd, buf, n)`: the kernel appends atomically for each call | `ofstream(path, ios::app)`; `write(buf, n); flush();` | `OpenOptions::new().append(true)`; `write_all(buf)` |
| `fflush(f)` pushes libc's buffer to the **OS** only | `stream.flush()` the same | `File` has no user-space buffer: `flush()` is a no-op; use `sync_all` for the disk |
| `fsync(fd)` / `fdatasync(fd)` to reach the device | `fsync` via the native handle | `file.sync_all()` / `file.sync_data()` |
| short writes: `write` can return less than `n`; loop | `write` sets `badbit` on failure | `write_all` loops for you |

**Port rule:** if the C++ calls `flush()` and the comment says "make it durable", the Rust translation is `sync_data`/`sync_all`, **not** `flush`. (BusTub's own `flush()` is not durable.)

### Learn more
- [`io::Write`](https://doc.rust-lang.org/std/io/trait.Write.html) · CMU 15-445 lecture "Database Logging"

## Part 3 · read_log: read from an offset

**Where this fits.** Recovery will read the log back from the start. This is the reader.

### The task

Implement `read_log(buf, offset)` in `src/storage/disk/disk_manager.rs` It reads `buf.len()` bytes of the log starting at byte `offset`:
- if `offset` is **at or past the end** of the log: return `Ok(false)` and leave `buf` untouched;
- otherwise return `Ok(true)`; whatever the log doesn't have (a read running off the end) is **zero-filled**.

### Tests

- `read_log` reads from an offset, returns `false` at or past the end with the buffer untouched, and zero-pads a short tail while returning `true`.

### Syntax and methods

```rust
log.metadata()?.len()               // the log's current length: u64
let n = read_full_at(&log, buf, offset)?;   // you wrote this in stage 6
buf[n..].fill(0);
```

### In BusTub

```cpp
auto DiskManager::ReadLog(char *log_data, int size, int offset) -> bool {
  if (offset >= GetFileSize(log_file_name_)) { return false; }
  log_io_.seekp(offset);
  log_io_.read(log_data, size);
  int read_count = log_io_.gcount();
  if (read_count < size) { log_io_.clear(); memset(log_data + read_count, 0, size - read_count); }
  return true;
}
```

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `fstat(fd, &st); st.st_size` or `lseek(fd, 0, SEEK_END)` | `GetFileSize(path)` (a `stat` call by name) | `file.metadata()?.len()` |
| `pread` + zero the missing tail with `memset` | `seekp(off); read(); gcount(); clear(); memset()` | `read_full_at` + `buf[n..].fill(0)` |
| returns `bool` for "no data" and logs I/O errors | `auto ReadLog(...) -> bool` | `io::Result<bool>`: an error is an `Err`, "nothing there" is `Ok(false)` |

**Pitfall in the C++:** `seekp` is the *put* position and `seekg` the *get* position; for an `fstream` they are linked, but for separate `ifstream`/`ofstream` objects they are not.
BusTub's `ReadLog` calls `seekp` and then reads: it works only because it is one `fstream`. Positional `read_at` has no such trap.

### Learn more
- [`File::metadata`](https://doc.rust-lang.org/std/fs/struct.File.html#method.metadata)

## Performance

A counter increment is one atomic read-modify-write (`lock xadd` on x86): no lock, no syscall. `write_log` is one `write` to a file opened with append, one syscall per call; `read_log` is a `fstat` for the length and one `pread`.

Two costs to know. Threads incrementing the *same* counter contend for one cache line, so a counter shared by many cores is slower than the instruction suggests; for statistics that is acceptable, and the usual remedy is per-thread counters summed on read. And one `write` per log record is expensive when records are small: batching several records into one `write` (group commit) is the standard fix, which you meet in module 5.

**Measure it.** Increment one counter 1 000 000 times from 1 thread and from 8 threads and compare the time per increment. `strace -c -e trace=write` while appending 1 000 records shows one `write` per record.

## Hints

### Count when it succeeded, with the weakest ordering that is correct

`Ordering::Relaxed` is enough for statistics: no other memory is published through these counters. C++'s `std::atomic` defaults to sequential consistency, which is stronger than needed. The more important decision is *placement*: increment after the write succeeded, so a failing write does not inflate `get_num_writes`; and a `write_log` of zero bytes is not a flush at all.

### The log has two cursors that must not meet

The log is opened for append, so every write lands at the end of the file atomically whatever any reader is doing. Reads use explicit offsets and never move a cursor. `read_log` returns `false` at or past the end of the log (the recovery loop's termination condition) and `true` with a zero-padded tail when the log ends mid-buffer, so a caller must decode lengths from the data and never trust `buf.len()`.
