You are building the bottom of the database: one file that holds fixed-size pages. This stage is the file's geometry and its opening: where slot `i` starts, how big the file must be to hold `n` pages, and `DiskManager::new`, which creates (and never truncates) the database file and its log and reserves room for 16 pages up front. Get the arithmetic right with `u64`s and the open flags right, because every byte written later depends on them.

> [!TIP] Look at the bytes
> Open the file you are writing: `xxd -l 64 test.db` shows the first bytes, and `ls -ls test.db` prints the *allocated* size next to the apparent size, so you can see that `set_len` makes a sparse file (blocks are only allocated when written).

## Part 1 · Compute a slot's byte offset

**Where this fits.** The disk manager stores pages in a file. Before any I/O, one question: where in the file does a page go?

### The task

The db file is a row of equal-sized **slots**, one page each: slot 0 is bytes `0..8192`, slot 1 is `8192..16384`, and so on.
Implement `slot_offset(slot)` in `src/storage/disk/disk_manager.rs`: the byte where slot `slot` starts. Slot numbers are `usize`; file offsets are `u64`.

### Tests

- `slot_offset(slot)` is `slot * 8192` as a `u64`, including slot `1_000_000`, which starts past 32 bits.

### Syntax and methods

| | |
|---|---|
| `x as u64` | numeric cast. There is no `From<usize> for u64` (a `usize` might be wider one day), so you cast |
| `slot as u64 * BUSTUB_PAGE_SIZE as u64` | `as` binds tighter than `*`: both sides become `u64`, then multiply |
| `BUSTUB_PAGE_SIZE` | a `usize` constant in `src/common/config.rs` |

### Notes

In debug builds integer overflow **panics**; in release it wraps. Doing the arithmetic in `u64` makes neither a worry for any real file.

### In BusTub

```cpp
return pages_.size() * BUSTUB_PAGE_SIZE;        // AllocatePage(): the offset of a fresh slot
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `(size_t)slot * PAGE_SIZE`, `static_cast<uint64_t>(slot) * kPageSize` | `slot as u64 * BUSTUB_PAGE_SIZE as u64` |
| `off_t` (signed, 64-bit on modern systems), `size_t` (unsigned, pointer-sized) | `i64` / `u64`, `usize` |
| implicit conversions and integer promotion between `int`, `long`, `size_t` | none: every conversion is written (`as`, `From`, `try_from`) |
| signed overflow is **undefined behaviour** (`int * int` that overflows) | debug: panic; release: wraps; or choose `checked_mul` / `wrapping_mul` / `saturating_mul` |

**The classic bug when porting:** `int offset = slot * PAGE_SIZE;` in C. If `slot` is an `int`, the multiplication happens in `int` and overflows
long before the result is widened. Cast one operand to the wide type *first*. Rust makes you write the type, so the bug can't hide.

### Learn more
- The Rust Reference: [type cast expressions](https://doc.rust-lang.org/reference/expressions/operator-expr.html#type-cast-expressions)
- BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp)

## Part 2 · Size a file for N pages

**Where this fits.** The db file is created with room for a number of pages. How many bytes is that?

### The task

Implement `file_size_for(capacity)` in `src/storage/disk/disk_manager.rs`: the byte length of a db file with room for `capacity` pages. BusTub keeps **one spare page** at the end, so the length is `capacity + 1` pages. Reuse `slot_offset`.

### Tests

- `file_size_for(n)` is `n + 1` pages: `8192` for 0, `139264` for 16.

### Syntax and methods

Nothing new: a function call. `slot_offset(n)` is "the offset where slot `n` starts", which is also "the length of a file that holds `n` slots".

### In BusTub

```cpp
std::filesystem::resize_file(db_file_name_, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `#define BUSTUB_PAGE_SIZE 8192` (macro, untyped, no scope) | `pub const BUSTUB_PAGE_SIZE: usize = 8192;` (typed, scoped, in `config.rs`) |
| `static constexpr int BUSTUB_PAGE_SIZE = 8192;` (BusTub's `config.h`) | same; and a `const fn` can use it at compile time |
| `(capacity + 1) * kPageSize` in `int` arithmetic | `slot_offset(capacity + 1)`: reuse the function that already does the widening |

**Port rule:** C/C++ constants that size buffers become `const`s of type `usize`; sizes that are file offsets become `u64`.

### Learn more
- BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp), constructor and `AllocatePage`

## Part 3 · Open (or create) the db file and the log file

**Where this fits.** `DiskManager::new` opens the two files everything else uses: the database file and its log.

### The task

`DiskManager::new(db_file)` opens `db_file` for reading and writing, **creating it if it isn't there and keeping its contents if it is**. It also opens a log file next to it: the same path with the extension replaced by `.log` (`test.bustub` → `test.log`), opened for reading and **appending**. If either can't be opened, `new` returns the `io::Error`; it does not panic.

`new` is yours to write whole, in `src/storage/disk/disk_manager.rs`: open both files and build the `DiskManager`. The struct and its fields are given as a starting point: keep them, or change them if you prefer another design. The tests only call `new`, `db_file_name()` and `log_file_name()` (and, later, the other public methods).

### Tests

- After `new` both files exist (`test.bustub` gets `test.log`, `my.data.db` gets `my.data.log`); an existing database keeps its bytes; a path in a missing directory is `NotFound`.

### Syntax and methods

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

### Notes

`?` works because `new` returns `io::Result<DiskManager>`. `append(true)` means every write lands at the current end of the file no matter what offset you give: right for a log.

### In BusTub

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

### The C/C++ way
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

### Learn more
- [`OpenOptions`](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html) · [`Path::with_extension`](https://doc.rust-lang.org/std/path/struct.Path.html#method.with_extension) · [`io::ErrorKind`](https://doc.rust-lang.org/std/io/enum.ErrorKind.html)
- The Rust Book: [recoverable errors with `Result` and `?`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)

## Part 4 · Give the db file room with set_len

**Where this fits.** A new db file starts with room for `DEFAULT_DB_IO_SIZE` pages, and the disk manager can say how big the file is.

### The task

In `src/storage/disk/disk_manager.rs`:
- in `DiskManager::new`, after opening, make the db file `file_size_for(DEFAULT_DB_IO_SIZE)` bytes long;
- `get_db_file_size()` returns the db file's length in bytes right now. It may `expect` that the file exists.

### Tests

- A new database is `17 * 8192` bytes, `get_db_file_size()` agrees with the file system, and reopening it keeps its size and contents.

### Syntax and methods

```rust
file.set_len(n_bytes)?;                           // io::Result<()>: the file is now exactly n bytes; new bytes are zero
let len: u64 = std::fs::metadata(&path)?.len();   // a file's size, by path
opt_or_result.expect("message")                   // unwrap, with your message in the panic
```

### Notes

Operating systems store a file that was extended this way **sparsely**: the zero bytes take no disk blocks until something is written there (compare `ls -l` and `ls -ls`). Extending is nearly free; that's why BusTub does it up front.

### In BusTub

```cpp
std::filesystem::resize_file(db_file, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
...
auto DiskManager::GetFileSize(const std::string &file_name) -> int {
  struct stat stat_buf;
  int rc = stat(file_name.c_str(), &stat_buf);
  return rc == 0 ? static_cast<int>(stat_buf.st_size) : -1;   // an int: files over 2 GB overflow; -1 for "error"
}
```

The port returns `u64` and treats a vanished db file as a bug, instead of returning `-1` for callers to forget to check.

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `ftruncate(fd, len)`; `std::filesystem::resize_file(path, len)` | `file.set_len(len)` |
| `posix_fallocate(fd, 0, len)` (really reserves blocks; not sparse) | no std equivalent (use `rustix::fs::fallocate`) |
| `struct stat st; stat(path, &st); st.st_size`, `fstat(fd, &st)` | `fs::metadata(path)?.len()`, `file.metadata()?.len()` |
| BusTub's `GetFileSize` returns `int` (-1 on error) | return `u64`; errors are `Result`, never an in-band `-1` |

**Pitfall in the C++:** `static_cast<int>(st.st_size)` silently truncates files over 2 GiB, and `-1` is a legal-looking size. Both are impossible here.

### Learn more
- [`File::set_len`](https://doc.rust-lang.org/std/fs/struct.File.html#method.set_len) · [`fs::metadata`](https://doc.rust-lang.org/std/fs/fn.metadata.html)

## Performance

Everything in this stage is O(1) arithmetic plus three system calls in `new`: two `open`s and one `set_len`. Nothing is written. Because `set_len` makes a *sparse* file, reserving room for 17 pages costs one syscall and no disk blocks; the blocks arrive when pages are written.

The obvious alternative, writing 17 zeroed pages to fill the file, is 17 `write` calls and 136 KiB of real I/O that buys nothing, and it makes the file look "used" to `du`.

**Measure it.** `ls -ls test.db` shows allocated blocks next to the apparent size: before the first page write the block count is 0 (or close to it, depending on the file system) while the size is `139264`. On Linux, `strace -c cargo test s1a_01` counts the syscalls your `new` makes; compare a version that zero-fills.

## Hints

### Draw the file before you touch an API

Slot `i` occupies bytes `[i·P, (i+1)·P)`. Offsets, the file size and what a read past the end means are all consequences of that picture. Before writing `new`, answer: what is the file's length right after creation, and who guarantees the first page write does not have to extend it? BusTub reserves `DEFAULT_DB_IO_SIZE` pages up front, because growing a file is a syscall with its own cost and failure mode, and you would rather pay it rarely and in one place.

### Opening a file has an order of failure

You open two files; if the second fails, the first must not leak. In Rust the first is dropped when the error returns, with no cleanup code, whereas in C++ you close it by hand or wrap it in RAII. Check the flags too: `create(true)` needs write or append access, `truncate(false)` is what stops opening an existing database from erasing it, and the log needs `append` so that the kernel, not your code, makes every write land at the end.
