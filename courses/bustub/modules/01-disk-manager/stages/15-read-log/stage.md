**Where this fits.** Recovery will read the log back from the start. This is the reader.

## The task

Implement `read_log(buf, offset)` in `src/storage/disk/disk_manager.rs` It reads `buf.len()` bytes of the log starting at byte `offset`:
- if `offset` is **at or past the end** of the log: return `Ok(false)` and leave `buf` untouched;
- otherwise return `Ok(true)`; whatever the log doesn't have (a read running off the end) is **zero-filled**.

## Tests

- A record reads back; `abc` + `def` read from offset 0 (6 bytes) and from offset 3 (`def`).
- An empty log, or an offset at/after the end, gives `false` and leaves the buffer as it was.
- `hi` read into 8 bytes gives `hi` then six zeros, and `true`.
- After reopening, old records are still readable.

## Syntax and methods

```rust
log.metadata()?.len()               // the log's current length: u64
let n = read_full_at(&log, buf, offset)?;   // you wrote this in stage 6
buf[n..].fill(0);
```

## In BusTub

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

## The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `fstat(fd, &st); st.st_size` or `lseek(fd, 0, SEEK_END)` | `GetFileSize(path)` (a `stat` call by name) | `file.metadata()?.len()` |
| `pread` + zero the missing tail with `memset` | `seekp(off); read(); gcount(); clear(); memset()` | `read_full_at` + `buf[n..].fill(0)` |
| returns `bool` for "no data" and logs I/O errors | `auto ReadLog(...) -> bool` | `io::Result<bool>`: an error is an `Err`, "nothing there" is `Ok(false)` |

**Pitfall in the C++:** `seekp` is the *put* position and `seekg` the *get* position; for an `fstream` they are linked, but for separate `ifstream`/`ofstream` objects they are not.
BusTub's `ReadLog` calls `seekp` and then reads: it works only because it is one `fstream`. Positional `read_at` has no such trap.

## Learn more
- [`File::metadata`](https://doc.rust-lang.org/std/fs/struct.File.html#method.metadata)
