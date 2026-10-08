**Where this fits.** The disk manager has a second file: the **write-ahead log** (the Recovery module builds the real one). For now it is a byte stream you can append to.

## The task

Implement `write_log(data)` in `src/storage/disk/disk_manager.rs` (the empty check and the lock are given): append `data` to the log file, and count one flush.

## Tests

- Two writes `abc` and `def` leave `abcdef` in `test.log`; the db file is untouched.
- Each non-empty write is one flush (5 writes, 5 flushes); an empty write is none.
- Opening the disk manager again keeps the old records and appends after them.

## Syntax and methods

```rust
use std::io::Write;
let mut log = self.log_io.lock().unwrap();   // `mut`: Write::write_all takes &mut self
log.write_all(data)?;                        // io::Result<()>
```

## Notes

The file was opened with `append(true)`, so each `write_all` lands at the end regardless of anything else. Appending is also the fastest way to write to a disk, which is why logs are append-only.

## In BusTub

```cpp
void DiskManager::WriteLog(char *log_data, int size) {
  if (size == 0) { return; }   // no effect on num_flushes_ if log buffer is empty
  num_flushes_ += 1;
  log_io_.write(log_data, size);   // sequence write
  log_io_.flush();                 // flushes the *stream's* buffer to the OS; not an fsync
}
```

## The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `open(.., O_WRONLY \| O_APPEND)`; `write(fd, buf, n)`: the kernel appends atomically for each call | `ofstream(path, ios::app)`; `write(buf, n); flush();` | `OpenOptions::new().append(true)`; `write_all(buf)` |
| `fflush(f)` pushes libc's buffer to the **OS** only | `stream.flush()` the same | `File` has no user-space buffer: `flush()` is a no-op; use `sync_all` for the disk |
| `fsync(fd)` / `fdatasync(fd)` to reach the device | `fsync` via the native handle | `file.sync_all()` / `file.sync_data()` |
| short writes: `write` can return less than `n`; loop | `write` sets `badbit` on failure | `write_all` loops for you |

**Port rule:** if the C++ calls `flush()` and the comment says "make it durable", the Rust translation is `sync_data`/`sync_all`, **not** `flush`. (BusTub's own `flush()` is not durable.)

## Learn more
- [`io::Write`](https://doc.rust-lang.org/std/io/trait.Write.html) · CMU 15-445 lecture "Database Logging"
