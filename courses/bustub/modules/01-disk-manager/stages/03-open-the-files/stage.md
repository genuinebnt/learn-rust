**Where this fits.** `DiskManager::new` opens the two files everything else uses: the database file and its log.

## The task

`DiskManager::new(db_file)` opens `db_file` for reading and writing, **creating it if it isn't there and keeping its contents if it is**. It also opens a log file next to it: the same path with the extension replaced by `.log` (`test.bustub` → `test.log`), opened for reading and **appending**. If either can't be opened, `new` returns the `io::Error`; it does not panic.

`new` is yours to write whole, in `src/storage/disk/disk_manager.rs`: open both files and build the `DiskManager`. The struct and its fields are given as a starting point: keep them, or change them if you prefer another design. The tests only call `new`, `db_file_name()` and `log_file_name()` (and, later, the other public methods).

## Tests

- After `new`, both files exist; the log is named `test.log` for `test.bustub`, `my.data.log` for `my.data.db`, `plain.log` for `plain`.
- An existing db file keeps its first bytes.
- A path in a directory that doesn't exist gives `ErrorKind::NotFound`; a path that is a directory is an error.

## Syntax and methods

```rust
use std::fs::OpenOptions;

let f = OpenOptions::new()      // a builder: every call takes and returns &mut OpenOptions
    .read(true)
    .write(true)
    .create(true)               // create if missing (needs write or append)
    .truncate(false)            // say it out loud: never wipe an existing file
    .open(&path)?;              // io::Result<File>; `?` returns the error from the function

OpenOptions::new().read(true).append(true).create(true).open(&path)?   // every write goes to the end

let log_path: PathBuf = path.with_extension("log");                    // "a/test.bustub" -> "a/test.log"
```

## Notes

`?` works because `new` returns `io::Result<DiskManager>`. `append(true)` means every write lands at the current end of the file no matter what offset you give: right for a log.

## In BusTub

```cpp
log_file_name_ = db_file_name_.filename().stem().string() + ".log";   // relative to the working directory!
log_io_.open(log_file_name_, std::ios::binary | std::ios::in | std::ios::app | std::ios::out);
if (!log_io_.is_open()) {            // didn't exist: create it
  log_io_.clear();
  log_io_.open(log_file_name_, std::ios::binary | std::ios::trunc | std::ios::out | std::ios::in);
  if (!log_io_.is_open()) throw Exception("can't open dblog file");
}
```

C++ opens, checks, and opens again to create; `create(true)` is the whole dance. An `Exception` becomes an `Err`. This port puts the log **next to the db file**, not in the current directory.

## The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `open(path, O_RDWR \| O_CREAT, 0644)` | `fstream.open(path, in \| out \| binary)` | `OpenOptions::new().read(true).write(true).create(true).open(path)` |
| `O_APPEND` | `std::ios::app` | `.append(true)` |
| `O_TRUNC` | `std::ios::trunc` | `.truncate(true)` (never implied: you must ask) |
| `O_CREAT \| O_EXCL` | (C++23 `noreplace`) | `.create_new(true)` |
| returns `-1`, error in the global `errno` | `is_open()`, `fail()`, exceptions if enabled | `io::Result<File>`; `e.kind()`, `e.raw_os_error()` |
| `close(fd)`, easy to forget or double-close | destructor closes | `Drop` closes; the file can't be used after it is dropped |
| `char *` paths, `dirname`, `basename` | `std::filesystem::path`: `.stem()`, `.extension()`, `.replace_extension()` | `Path`/`PathBuf`: `.file_stem()`, `.extension()`, `.with_extension()` |

**Pitfalls ported away:** forgetting to check `open`'s `-1`; leaking the fd on an early return (RAII fixes this in C++ too, but a raw `int fd` doesn't);
using the fd after `close`. In Rust the `File` owns the descriptor.

## Learn more
- [`OpenOptions`](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html) · [`Path::with_extension`](https://doc.rust-lang.org/std/path/struct.Path.html#method.with_extension) · [`io::ErrorKind`](https://doc.rust-lang.org/std/io/enum.ErrorKind.html)
- The Rust Book: [recoverable errors with `Result` and `?`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
