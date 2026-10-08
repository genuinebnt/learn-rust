**Where this fits.** The first real I/O: put one page into the file.

## The task

Implement `write_slot(file, slot, data)` in `src/storage/disk/disk_manager.rs`: write the whole `data` page at the slot's byte offset. One line.

## Tests

- Writing slot 2 into an empty file makes it 3 pages long; slots 0 and 1 are a hole of zeros.
- Writing slot 1 twice replaces the page in place; neighbours aren't disturbed; the order of writes doesn't matter.
- A file opened read-only gives an error.

## Syntax and methods

```rust
use std::os::unix::fs::FileExt;     // adds read_at / write_at / write_all_at to File (macOS and Linux)

file.write_all_at(&bytes, offset)?; // bytes: &[u8]; offset: u64; io::Result<()>
```

`data` is a `&PageData`, that is `&[u8; 8192]`; it converts to `&[u8]` where a slice is wanted. Writing past the end extends the file.

## Notes

There are two ways to write somewhere in a file. **Seek then write**: `seek` moves the file's one shared cursor, then `write` writes there. That is two steps, and two threads using the same open file can interleave them (it compiles, because `&File` implements `Seek` and `Write`, and it is still a race). A **positional write** (`pwrite`) says "write these bytes at this offset" in one call, with no cursor at all. `write_at` may write fewer bytes than given; `write_all_at` repeats until every byte is written.

## In BusTub

```cpp
db_io_.seekp(offset);                         // move the stream's cursor
db_io_.write(page_data, BUSTUB_PAGE_SIZE);    // write there
```

Two calls on a shared stream: this is why BusTub guards the whole file with `db_io_latch_`.

## The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `pwrite(fd, buf, n, offset)` returns `ssize_t`; may write **less than `n`** | | `file.write_at(buf, offset)` (the same, returns `usize`) |
| a loop around `pwrite`, retrying on `EINTR` | | `file.write_all_at(buf, offset)` |
| `lseek(fd, off, SEEK_SET)` then `write(fd, ..)`: shared offset, racy between threads | `stream.seekp(off); stream.write(buf, n);` | `Seek::seek` + `Write::write_all`: compiles even on a shared `&File`, and is racy for the same reason |
| `fseek(f, off, SEEK_SET); fwrite(buf, 1, n, f);` (buffered by libc) | | `BufWriter<File>` if you want user-space buffering; `File` itself is unbuffered |

**The big idea:** prefer `pread`/`pwrite` over `lseek` + `read`/`write` when several threads share one descriptor: the offset is an argument, not state.

## Learn more
- [`FileExt`](https://doc.rust-lang.org/std/os/unix/fs/trait.FileExt.html) · `man 2 pwrite`
