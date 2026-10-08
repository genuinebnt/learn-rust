You are building the bottom of the database: one file that holds fixed-size pages. By the end `DiskManager::new` opens the database file and its log, `write_slot` and `read_slot` move one page between memory and a byte range of the file, and the file is sized so that no slot computation walks off its end. Nothing here knows about page ids yet; that mapping is the next stage.

The seven parts are one idea at increasing risk: *where* a page lives (offsets), *how big* the file is, *what can fail* when opening it, and then the I/O primitives and their one real hazard, the short read. The tests are strict about the edges (a page past the end of the file reads as zeros, a short read reports exactly how many bytes the file had) because every layer above assumes them.

Work through the parts in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Compute a slot's byte offset

**Where this fits.** The disk manager stores pages in a file. Before any I/O, one question: where in the file does a page go?

### The task

The db file is a row of equal-sized **slots**, one page each: slot 0 is bytes `0..8192`, slot 1 is `8192..16384`, and so on.
Implement `slot_offset(slot)` in `src/storage/disk/disk_manager.rs`: the byte where slot `slot` starts. Slot numbers are `usize`; file offsets are `u64`.

### Tests

- `slot_offset(0)` is `0`; `slot_offset(1)` is `8192`; `slot_offset(3)` is `3 * 8192`.
- Slot `1_000_000` starts at byte `8_192_000_000`, which doesn't fit in 32 bits.

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

- `file_size_for(0)` is one page, `8192`.
- `file_size_for(16)` is `17 * 8192` = `139264`.
- `file_size_for(32) - file_size_for(16)` is 16 pages.

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

- After `new`, both files exist; the log is named `test.log` for `test.bustub`, `my.data.log` for `my.data.db`, `plain.log` for `plain`.
- An existing db file keeps its first bytes.
- A path in a directory that doesn't exist gives `ErrorKind::NotFound`; a path that is a directory is an error.

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

- A new db file is `17 * 8192` bytes, and `get_db_file_size()` agrees with `std::fs::metadata`.
- The new room reads as zeros; opening the same file again keeps the size and any bytes already inside it.

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

## Part 5 · Write a page at a slot with write_all_at

**Where this fits.** The first real I/O: put one page into the file.

### The task

Implement `write_slot(file, slot, data)` in `src/storage/disk/disk_manager.rs`: write the whole `data` page at the slot's byte offset. One line.

### Tests

- Writing slot 2 into an empty file makes it 3 pages long; slots 0 and 1 are a hole of zeros.
- Writing slot 1 twice replaces the page in place; neighbours aren't disturbed; the order of writes doesn't matter.
- A file opened read-only gives an error.

### Syntax and methods

```rust
use std::os::unix::fs::FileExt;     // adds read_at / write_at / write_all_at to File (macOS and Linux)

file.write_all_at(&bytes, offset)?; // bytes: &[u8]; offset: u64; io::Result<()>
```

`data` is a `&PageData`, that is `&[u8; 8192]`; it converts to `&[u8]` where a slice is wanted. Writing past the end extends the file.

### Notes

There are two ways to write somewhere in a file. **Seek then write**: `seek` moves the file's one shared cursor, then `write` writes there. That is two steps, and two threads using the same open file can interleave them (it compiles, because `&File` implements `Seek` and `Write`, and it is still a race). A **positional write** (`pwrite`) says "write these bytes at this offset" in one call, with no cursor at all. `write_at` may write fewer bytes than given; `write_all_at` repeats until every byte is written.

### In BusTub

```cpp
db_io_.seekp(offset);                         // move the stream's cursor
db_io_.write(page_data, BUSTUB_PAGE_SIZE);    // write there
```

Two calls on a shared stream: this is why BusTub guards the whole file with `db_io_latch_`.

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `pwrite(fd, buf, n, offset)` returns `ssize_t`; may write **less than `n`** | | `file.write_at(buf, offset)` (the same, returns `usize`) |
| a loop around `pwrite`, retrying on `EINTR` | | `file.write_all_at(buf, offset)` |
| `lseek(fd, off, SEEK_SET)` then `write(fd, ..)`: shared offset, racy between threads | `stream.seekp(off); stream.write(buf, n);` | `Seek::seek` + `Write::write_all`: compiles even on a shared `&File`, and is racy for the same reason |
| `fseek(f, off, SEEK_SET); fwrite(buf, 1, n, f);` (buffered by libc) | | `BufWriter<File>` if you want user-space buffering; `File` itself is unbuffered |

**The big idea:** prefer `pread`/`pwrite` over `lseek` + `read`/`write` when several threads share one descriptor: the offset is an argument, not state.

### Learn more
- [`FileExt`](https://doc.rust-lang.org/std/os/unix/fs/trait.FileExt.html) · `man 2 pwrite`

## Part 6 · Read until the buffer is full: read_full_at

**Where this fits.** The mirror of the last stage, with one wrinkle: a read can return fewer bytes than you asked for.

### The task

Implement `read_full_at(file, buf, offset)` in `src/storage/disk/disk_manager.rs`: read from byte `offset` into `buf` until `buf` is full or the file ends, and return **how many bytes it read**. That is `buf.len()` unless the file ended first.

### Tests

- A 10-byte file read into a 4-byte buffer at offset 0, 8 and 10 returns 4, 2 and 0; at offset 1000 returns 0.
- Bytes of the buffer beyond what was read are left alone.
- An empty buffer returns 0. A 3 MB read comes back complete (one `read_at` call won't deliver it all).

### Syntax and methods

```rust
let n = file.read_at(&mut buf[filled..], offset + filled as u64)?;   // &mut buf[filled..] is the unfilled tail

match file.read_at(/* .. */) {
    Ok(0) => break,                                                    // end of file
    Ok(n) => filled += n,                                              // got some; ask again for the rest
    Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,      // a signal arrived: just retry
    Err(e) => return Err(e),
}
```

### Notes

`read_at` fills **up to** `buf.len()` bytes and returns how many. It can return less even though the file has more (the OS may hand back a partial read), and it returns `Ok(0)` only at the end of the file. So a "read this many bytes" operation is a loop. (The standard library's `read_exact_at` is that loop, but it turns a short file into an error; here a short file is a normal answer.)

### In BusTub

```cpp
db_io_.read(page_data, BUSTUB_PAGE_SIZE);
int read_count = db_io_.gcount();       // how many bytes actually arrived
```

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `pread(fd, buf, n, off)`: returns bytes read, `0` at end of file, `-1` on error (check `errno`) | `stream.read(buf, n); stream.gcount()` | `file.read_at(buf, off)` → `io::Result<usize>`; `Ok(0)` is EOF |
| `if (r < 0 && errno == EINTR) continue;` | | `Err(e) if e.kind() == ErrorKind::Interrupted => continue` |
| `fread(buf, 1, n, f)` returns a count; `feof(f)` / `ferror(f)` tell *why* it was short | `stream.eof()`, `stream.fail()`, `stream.clear()` | no hidden state: the `Result` and the `usize` are the whole answer |
| `readn()` / "read exactly n" helper from Stevens' *UNIX Network Programming* | | `read_exact_at` (errors on short read) or your own loop (returns the count) |

**Pitfall in the C++ streams:** reading past the end sets `failbit`/`eofbit`, and every later operation silently does nothing until you call `clear()`
(BusTub calls it for exactly this reason). Rust has no sticky stream state.

### Learn more
- [`FileExt::read_at`](https://doc.rust-lang.org/std/os/unix/fs/trait.FileExt.html#tymethod.read_at) (read the note on short reads) · [`io::ErrorKind::Interrupted`](https://doc.rust-lang.org/std/io/enum.ErrorKind.html#variant.Interrupted)

## Part 7 · Read a slot, zero-filling what the file lacks

**Where this fits.** A page that was never written, or only partly written, must read as zeros.

### The task

Implement `read_slot(file, slot, buf)` in `src/storage/disk/disk_manager.rs`: read the slot into `buf` with `read_full_at`, then set **every byte it didn't fill** to `0`. The buffer may hold anything on the way in.

### Tests

- A slot written with `write_slot` reads back identical.
- A 100-byte file read as slot 0: the first 100 bytes come back, the other 8092 are zero (even if the buffer was full of `0xFF`).
- A slot far past the end is all zeros. A slot that ends exactly at the end of the file needs no filling.

### Syntax and methods

```rust
buf[n..].fill(0);        // set every element of a slice to a value; n == buf.len() is fine (empty slice)
```

### In BusTub

```cpp
if (read_count < BUSTUB_PAGE_SIZE) {
    db_io_.clear();                                              // un-fail the stream after hitting EOF
    memset(page_data + read_count, 0, BUSTUB_PAGE_SIZE - read_count);
}
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `memset(buf + n, 0, size - n);` | `buf[n..].fill(0);` |
| if `n > size`, `size - n` wraps (it's unsigned) and `memset` writes gigabytes: **a buffer overflow** | `buf[n..]` panics on `n > len` (a bounds check); never memory corruption |
| `char buf[PAGE_SIZE]` decays to `char *` and forgets its length when passed to a function | `&mut PageData` is `&mut [u8; 8192]`: the length is part of the type |
| `std::array<char, N>`, `std::span<char>` (C++20) | `[u8; N]`, `&mut [u8]` |

**Port rule:** `(char *p, size_t n)` pairs become one slice `&[u8]` / `&mut [u8]`; a pointer to a fixed-size buffer becomes `&[u8; N]`.

### Learn more
- [`<[T]>::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill)

## Hints

### Draw the file before you touch an API

Slot `i` occupies bytes `[i·P, (i+1)·P)`. Offsets, the file size and what a read past the end means are all consequences of that picture. Before writing `new`, answer: what is the file's length right after creation, and who guarantees the first page write does not have to extend it? BusTub reserves `DEFAULT_DB_IO_SIZE` pages up front, because growing a file is a syscall with its own cost and failure mode, and you would rather pay it rarely and in one place.

### A read is not a promise

`read_at` may return fewer bytes than the buffer holds even when more are in the file, and it can be interrupted. The contract of `read_full_at` is therefore a loop: stop when the buffer is full or `read_at` returns 0 (end of file), retry `Interrupted`, surface every other error. Then decide *where* the zero-fill of a short read lives. `read_slot` needs it (a page never written must read as zeros, because the buffer pool will treat it as a fresh page), but `read_full_at` must not do it: the log reader needs the true byte count, and a function that both fills and pads loses that information.

### Positional I/O versus seek-then-read

`write_all_at` and `read_at` take the offset as an argument and leave the file cursor alone, so two threads cannot interleave "seek here" and "read there". With `seek` + `read` you would have to hold a lock across both calls. The C++ way, `seekp` followed by `write` on a shared `fstream`, has exactly that race. You will be glad of positional I/O in the scheduler module, where several workers touch the same file.

### Opening a file has an order of failure

You open two files; if the second fails, the first must not leak. In Rust the first is dropped when the error returns, with no cleanup code, whereas in C++ you close it by hand or wrap it in RAII. Check the flags too: `create(true)` needs write or append access, `truncate(false)` is what stops opening an existing database from erasing it, and the log needs `append` so that the kernel, not your code, makes every write land at the end.
