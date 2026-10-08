---
title: Positional I/O, short reads and sparse files
summary: Why a file is read with an offset instead of a cursor, why a read can return less than you asked for, and what set_len really does.
minutes: 9
---
A database file is an array of pages that happens to live in the kernel. Everything the disk manager does is arithmetic on offsets plus four system-call habits. This page is those habits, with the C and C++ versions next to the Rust ones, because every one of them is a classic porting trap.

## A file is an array; a cursor is shared state

The file is a row of fixed-size **slots**: slot `i` occupies bytes `[i·P, (i+1)·P)`, with `P = BUSTUB_PAGE_SIZE = 8192`. Page 3 therefore starts at byte 24 576, and page 1 000 000 at byte 8 192 000 000, which does not fit in 32 bits. Offsets are `u64` (`off_t` in C, `std::streamoff` in C++), and the multiplication has to happen *after* widening:

```svg
caption: The file is an array of 8192-byte slots. Slot i starts at byte i × 8192, so slot 3 starts at byte 24 576.
<svg viewBox="0 0 760 170" role="img" aria-label="A file drawn as six equal slots with byte offsets under each boundary">
<rect class="box" x="24" y="64" width="112" height="46" rx="4"/><text class="mid" x="80" y="92">slot 0</text><rect class="box" x="142" y="64" width="112" height="46" rx="4"/><text class="mid" x="198" y="92">slot 1</text><rect class="box" x="260" y="64" width="112" height="46" rx="4"/><text class="mid" x="316" y="92">slot 2</text><rect class="hot" x="378" y="64" width="112" height="46" rx="4"/><text class="mid big" x="434" y="92">slot 3</text><rect class="box" x="496" y="64" width="112" height="46" rx="4"/><text class="mid" x="552" y="92">slot 4</text><rect class="box" x="614" y="64" width="112" height="46" rx="4"/><text class="mid" x="670" y="92">slot 5</text>
<line class="ln" x1="24" y1="110" x2="24" y2="124"/><text class="mid dim sm" x="24" y="140">0</text><line class="ln" x1="142" y1="110" x2="142" y2="124"/><text class="mid dim sm" x="142" y="140">8 192</text><line class="ln" x1="260" y1="110" x2="260" y2="124"/><text class="mid dim sm" x="260" y="140">16 384</text><line class="ln" x1="378" y1="110" x2="378" y2="124"/><text class="mid t-a sm" x="378" y="140">24 576</text><line class="ln" x1="496" y1="110" x2="496" y2="124"/><text class="mid dim sm" x="496" y="140">32 768</text><line class="ln" x1="614" y1="110" x2="614" y2="124"/><text class="mid dim sm" x="614" y="140">40 960</text><line class="ln" x1="732" y1="110" x2="732" y2="124"/><text class="mid dim sm" x="732" y="140">49 152</text>
<path class="ln-w" d="M378 52 v-8 h112 v8"/>
<text class="mid t-w" x="434" y="36">P = 8192 bytes</text>
<text class="t-a big" x="24" y="30">offset(slot) = slot × P</text>
<text class="dim sm" x="24" y="160">bytes from the start of the file</text>
</svg>
```

```rust
let offset = slot as u64 * BUSTUB_PAGE_SIZE as u64;   // widen first, then multiply
```

```cpp
off_t offset = slot * PAGE_SIZE;            // int * int overflows in int, then widens: the classic bug
off_t offset = (off_t)slot * PAGE_SIZE;     // correct
```

The old way to touch byte `offset` is two calls, `lseek(fd, offset, SEEK_SET)` then `read(fd, buf, n)`, or `seekg` then `read` on an `ifstream`. Both calls act on **the file's cursor**, which belongs to the open file, not to your thread. Two threads doing "seek here, read there" can interleave as seek, seek, read, read, and each reads the other's page. The classical fix is a lock around the pair. The better fix is a call that takes the offset as an argument:

| POSIX | C++ standard library | Rust (`std::os::unix::fs::FileExt`) |
|---|---|---|
| `pread(fd, buf, n, off)` | no equivalent (`fstream` only has a cursor) | `file.read_at(&mut buf, off)` |
| `pwrite(fd, buf, n, off)` | no equivalent | `file.write_at(&buf, off)` / `write_all_at` |
| `lseek` + `read` | `seekg` + `read` | `Seek::seek` + `Read::read` (shares the cursor: avoid) |

`pread` and `pwrite` do not read or move the cursor, so there is nothing to race on. The kernel serialises the I/O to the file itself; what you must still protect is *your own* bookkeeping (the page table), which is why the disk manager has a latch and the file I/O stays outside any lock-ordering puzzle.

> [!PORT] Windows
> `FileExt` is Unix-only. On Windows the equivalent is `std::os::windows::fs::FileExt::seek_read` and `seek_write`, which *do* move the cursor. This course targets macOS and Linux; a Windows port would put the file behind the same latch it already needs for the page table.

## A read is a request, not a promise

`read_at(buf, off)` returns `Ok(n)` with `0 ≤ n ≤ buf.len()`. Three different situations give `n < buf.len()`:

1. **End of file.** You asked for 8192 bytes at an offset 100 bytes before the end; you get 100. At or past the end you get `Ok(0)`.
2. **Interruption.** A signal arrives mid-call. Depending on the platform you get a short count or the error `Interrupted` (`EINTR`).
3. **The system simply returned less.** POSIX allows it for any file; regular files on local disks rarely do it, pipes, sockets and network file systems do it all the time.

```svg
caption: One read_at call may fill only part of the buffer, so read_full_at asks again from where the last call stopped. It stops when the buffer is full or a call returns 0 (end of file). (Animated.)
<svg viewBox="0 0 760 236" role="img" aria-label="A buffer filled by three successive reads of 3000, 4000 and 1192 bytes">
<style>
@keyframes sr1{0%{transform:scaleX(0);opacity:0}8%,92%{transform:scaleX(1);opacity:1}100%{transform:scaleX(0);opacity:0}}
@keyframes sr2{0%,18%{transform:scaleX(0);opacity:0}28%,92%{transform:scaleX(1);opacity:1}100%{transform:scaleX(0);opacity:0}}
@keyframes sr3{0%,40%{transform:scaleX(0);opacity:0}50%,92%{transform:scaleX(1);opacity:1}100%{transform:scaleX(0);opacity:0}}
@keyframes sr4{0%,56%{opacity:0}62%,92%{opacity:1}100%{opacity:0}}
.sr-a,.sr-b,.sr-c{transform-box:fill-box;transform-origin:left center}
.sr-a{animation:sr1 9s ease-out infinite}.sr-b{animation:sr2 9s ease-out infinite}.sr-c{animation:sr3 9s ease-out infinite}
.sr-l1{animation:sr1 9s linear infinite}.sr-l2{animation:sr2 9s linear infinite}.sr-l3{animation:sr3 9s linear infinite}.sr-l4{animation:sr4 9s linear infinite}
</style>
<text class="dim sm" x="20" y="22">buf: 8192 bytes</text>
<rect class="never" x="20" y="30" width="720" height="38" rx="3"/>
<rect class="sr-a blue" x="20" y="30" width="263.7" height="38" rx="3"/>
<rect class="sr-b violet" x="283.7" y="30" width="351.6" height="38" rx="3"/>
<rect class="sr-c live" x="635.3" y="30" width="104.7" height="38" rx="3"/>
<g class="sr-l1"><text class="t-b" x="20" y="104">call 1</text><text x="90" y="104">read_at(&amp;mut buf[0..], off)</text><text class="t-b end" x="740" y="104">Ok(3000)</text></g>
<g class="sr-l2"><text class="t-v" x="20" y="132">call 2</text><text x="90" y="132">read_at(&amp;mut buf[3000..], off + 3000)</text><text class="t-v end" x="740" y="132">Ok(4000)</text></g>
<g class="sr-l3"><text class="t-g" x="20" y="160">call 3</text><text x="90" y="160">read_at(&amp;mut buf[7000..], off + 7000)</text><text class="t-g end" x="740" y="160">Ok(1192)</text></g>
<g class="sr-l4"><line class="grid" x1="20" y1="176" x2="740" y2="176"/><text class="big t-g" x="20" y="204">filled == buf.len() &#8594; stop and return Ok(8192)</text><text class="dim sm" x="20" y="224">(had call 3 returned Ok(0), the file ended: stop and return what you have)</text></g>
</svg>
```

So the primitive you want is a loop that keeps asking until the buffer is full or the file says "no more":

```rust
pub fn read_full_at(file: &File, buf: &mut [u8], offset: u64) -> io::Result<usize> {
    let mut filled = 0;
    while filled < buf.len() {
        match file.read_at(&mut buf[filled..], offset + filled as u64) {
            Ok(0) => break,                                              // end of file
            Ok(n) => filled += n,
            Err(e) if e.kind() == io::ErrorKind::Interrupted => continue, // EINTR: just ask again
            Err(e) => return Err(e),
        }
    }
    Ok(filled)
}
```

Two details matter. `Interrupted` is retried, not reported: it carries no information about the file. And the function returns *how many bytes it got*, not a bool and not a padded buffer, because a caller that needs the truth (the log reader, later the recovery manager) cannot recover it from a buffer you silently zero-filled. Padding is a policy of `read_slot`, not of the primitive.

The writing side has the standard library's own version of this loop: `write_all_at` keeps writing until everything is out or an error occurs. In C you write the loop yourself; forgetting it is a long-standing source of silently truncated files.

> [!WARNING] The `fread` trap
> C's `fread(buf, 1, n, f)` returns a count that is *also* less than `n` at end of file *and* on error, and you must call `feof` or `ferror` to tell them apart. Rust returns the error as a `Result`; EOF is `Ok(0)`. Do not port the `feof`/`ferror` dance; port the loop.

## Reading what was never written

The buffer pool will ask for page 500 before anybody wrote it. It expects zeros, because a never-written page is a fresh page. Two mechanisms can give you that, and a good implementation uses both on purpose:

- **Past the end of the file**, a read returns 0 bytes and your code fills the rest of the buffer with zeros (`buf[n..].fill(0)`).
- **Inside the file but never written**, the kernel does it for you if the file was extended with `set_len`: the new region reads as zeros.

`set_len(size)` (`ftruncate`) changes the file's length. Growing it does not write anything. On most Unix file systems the new bytes are a *hole*: they have a length but no disk blocks, they read as zeros, and blocks are allocated only when somebody writes into them. That is a **sparse file**, and you can see it:

```sh
$ ls -ls test.db     # first column: blocks actually allocated; the size column: apparent length
  0 -rw-r--r--  1 you  staff  139264 Oct  8 10:00 test.db      # 17 slots of 8192, no blocks allocated yet
$ xxd -l 32 test.db  # reads as zeros even though nothing was written
```

This is why the disk manager can reserve room for `DEFAULT_DB_IO_SIZE` pages up front at no cost, and why it grows the file by *doubling* `set_len` rather than extending it a page at a time: growth is a metadata change, and you want few of them.

## Durability is a separate question

`write_all_at` hands bytes to the operating system's page cache. When it returns, a *process* crash cannot lose them, but a *power* failure can. Making them durable is a different call, `fsync` (`File::sync_all`, or `sync_data` to skip metadata), and it is expensive: it waits for the device. BusTub's disk manager calls it only at shutdown; a real storage engine calls it exactly where its recovery protocol says it must (module 5 is about that rule).

Note what Rust does *not* have: a user-space buffer inside `File`. In C++, `std::ofstream` buffers writes and needs `flush()`; in C, `FILE*` does the same. `std::fs::File` does not, so there is no flush to forget. If you wrap it in a `BufWriter` you have chosen to buffer, and then you do owe a flush.

## Opening a file: the flags that matter

| POSIX `open` flags | C++ `fstream` modes | Rust `OpenOptions` |
|---|---|---|
| `O_RDWR` | `in \| out` | `.read(true).write(true)` |
| `O_CREAT` | (implied by `out` when the file is missing) | `.create(true)` (needs write or append) |
| `O_TRUNC` | `trunc` (and implied by `out` alone: a famous surprise) | `.truncate(true)` (so say `false` to keep contents) |
| `O_APPEND` | `app` | `.append(true)` |

The two to remember: **never truncate the database file when opening it** (an existing database must survive a restart), and **open the log in append mode**, so that the *kernel* chooses the offset of each write atomically. An append-mode write goes to the end of the file no matter what any other writer is doing; that single property is what lets two threads append log records without overwriting each other.
