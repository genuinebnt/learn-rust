**Where this fits.** The mirror of the last stage, with one wrinkle: a read can return fewer bytes than you asked for.

## The task

Implement `read_full_at(file, buf, offset)` in `src/storage/disk/disk_manager.rs`: read from byte `offset` into `buf` until `buf` is full or the file ends, and return **how many bytes it read**. That is `buf.len()` unless the file ended first.

## Tests

- A 10-byte file read into a 4-byte buffer at offset 0, 8 and 10 returns 4, 2 and 0; at offset 1000 returns 0.
- Bytes of the buffer beyond what was read are left alone.
- An empty buffer returns 0. A 3 MB read comes back complete (one `read_at` call won't deliver it all).

## Syntax and methods

```rust
let n = file.read_at(&mut buf[filled..], offset + filled as u64)?;   // &mut buf[filled..] is the unfilled tail

match file.read_at(/* .. */) {
    Ok(0) => break,                                                    // end of file
    Ok(n) => filled += n,                                              // got some; ask again for the rest
    Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,      // a signal arrived: just retry
    Err(e) => return Err(e),
}
```

## Notes

`read_at` fills **up to** `buf.len()` bytes and returns how many. It can return less even though the file has more (the OS may hand back a partial read), and it returns `Ok(0)` only at the end of the file. So a "read this many bytes" operation is a loop. (The standard library's `read_exact_at` is that loop, but it turns a short file into an error; here a short file is a normal answer.)

## In BusTub

```cpp
db_io_.read(page_data, BUSTUB_PAGE_SIZE);
int read_count = db_io_.gcount();       // how many bytes actually arrived
```

## The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `pread(fd, buf, n, off)`: returns bytes read, `0` at end of file, `-1` on error (check `errno`) | `stream.read(buf, n); stream.gcount()` | `file.read_at(buf, off)` → `io::Result<usize>`; `Ok(0)` is EOF |
| `if (r < 0 && errno == EINTR) continue;` | | `Err(e) if e.kind() == ErrorKind::Interrupted => continue` |
| `fread(buf, 1, n, f)` returns a count; `feof(f)` / `ferror(f)` tell *why* it was short | `stream.eof()`, `stream.fail()`, `stream.clear()` | no hidden state: the `Result` and the `usize` are the whole answer |
| `readn()` / "read exactly n" helper from Stevens' *UNIX Network Programming* | | `read_exact_at` (errors on short read) or your own loop (returns the count) |

**Pitfall in the C++ streams:** reading past the end sets `failbit`/`eofbit`, and every later operation silently does nothing until you call `clear()`
(BusTub calls it for exactly this reason). Rust has no sticky stream state.

## Learn more
- [`FileExt::read_at`](https://doc.rust-lang.org/std/os/unix/fs/trait.FileExt.html#tymethod.read_at) (read the note on short reads) · [`io::ErrorKind::Interrupted`](https://doc.rust-lang.org/std/io/enum.ErrorKind.html#variant.Interrupted)
