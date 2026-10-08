Moving one page between memory and the file. `write_slot` is one positional write; `read_full_at` is the loop the kernel's `read` forces on you (a read may return less than you asked for); and `read_slot` turns "the file has fewer bytes than a page" into zeros, because the buffer pool will ask for pages nobody has written. The hazard in this stage is believing that a single `read_at` fills your buffer.

## Part 1 · Write a page at a slot with write_all_at

**Where this fits.** The first real I/O: put one page into the file.

### The task

Implement `write_slot(file, slot, data)` in `src/storage/disk/disk_manager.rs`: write the whole `data` page at the slot's byte offset. One line.

### Tests

- Writing slot 2 into an empty file makes it 3 pages long with slots 0 and 1 reading as zeros; rewriting a slot replaces it in place; a read-only file is an error.

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

## Part 2 · Read until the buffer is full: read_full_at

**Where this fits.** The mirror of the last stage, with one wrinkle: a read can return fewer bytes than you asked for.

### The task

Implement `read_full_at(file, buf, offset)` in `src/storage/disk/disk_manager.rs`: read from byte `offset` into `buf` until `buf` is full or the file ends, and return **how many bytes it read**. That is `buf.len()` unless the file ended first.

### Tests

- A 10-byte file read into a 4-byte buffer at offsets 0, 8 and 10 returns 4, 2 and 0; an empty buffer returns 0; a 3 MB read arrives complete.

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

## Part 3 · Read a slot, zero-filling what the file lacks

**Where this fits.** A page that was never written, or only partly written, must read as zeros.

### The task

Implement `read_slot(file, slot, buf)` in `src/storage/disk/disk_manager.rs`: read the slot into `buf` with `read_full_at`, then set **every byte it didn't fill** to `0`. The buffer may hold anything on the way in.

### Tests

- A slot reads back what was written; a slot the file only partly has comes back zero-padded, even into a buffer full of `0xFF`; a slot past the end is all zeros.

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

## Performance

A page write is one `pwrite` of 8 KiB and a page read is normally one `pread`: the loop in `read_full_at` iterates more than once only on a short read, so on a healthy file it costs one call plus a branch. Both are served from the operating system's page cache; neither waits for the device (that is `fsync`'s job).

The obvious version, `seek` then `read`, is two syscalls per page and a shared cursor to protect. Wrapping the file in a `BufReader` is worse for page I/O: it reads into its own buffer and then copies, so every 8 KiB page is copied twice.

**Measure it.** Write and read 10 000 slots in a loop and time it: expect a cost dominated by syscalls and copies, not by your code, and expect reads of recently written slots to be much faster than reads after dropping the cache (a cold read has to go to the device). `strace -c -e trace=pread64,pwrite64,lseek` (Linux) should show no `lseek` at all.

## Hints

### A read is not a promise

`read_at` may return fewer bytes than the buffer holds even when more are in the file, and it can be interrupted. The contract of `read_full_at` is therefore a loop: stop when the buffer is full or `read_at` returns 0 (end of file), retry `Interrupted`, surface every other error. Then decide *where* the zero-fill of a short read lives. `read_slot` needs it (a page never written must read as zeros), but `read_full_at` must not do it: the log reader needs the true byte count, and a function that both fills and pads loses that information.

### Positional I/O versus seek-then-read

`write_all_at` and `read_at` take the offset as an argument and leave the file cursor alone, so two threads cannot interleave "seek here" and "read there". With `seek` + `read` you would have to hold a lock across both calls. The C++ way, `seekp` followed by `write` on a shared `fstream`, has exactly that race. You will be glad of positional I/O in the scheduler module, where several workers touch the same file.
