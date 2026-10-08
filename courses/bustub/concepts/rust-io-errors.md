---
title: Errors from the operating system: io::Result, ? and panics
summary: How a failing system call becomes a Result, what ErrorKind lets you test for, the ? operator, and the line between an Err and a panic.
minutes: 8
---
Every disk operation can fail: the directory does not exist, the disk is full, a signal interrupts the call. C and C++ report that in three different ways, and the porting trap is that *forgetting to look* is silent in both.

## Three conventions

| | how failure is reported | what you forget |
|---|---|---|
| **C** | the call returns `-1` (or `NULL`) and sets the thread-local `errno`; you read it with `perror` or `strerror(errno)` | checking the return value: execution simply continues with garbage |
| **C++ streams** | `fstream` sets `failbit` or `badbit` and carries on; it only throws if you called `exceptions(...)` | checking `if (!file)`: reads return unchanged buffers |
| **C++ `<filesystem>`** | throws `std::filesystem::filesystem_error`, or fills a `std::error_code` out-parameter in the overloads that take one | catching the exception, or the out-parameter overload's error |
| **Rust** | returns `io::Result<T>` = `Result<T, io::Error>`: you cannot get the `T` without dealing with the `Err` | nothing: an unused `Result` is a compiler warning (`#[must_use]`) |

## What an `io::Error` holds

An `io::Error` wraps the OS error number (`errno` on Unix) and exposes it two ways: `raw_os_error()` gives the number, and `kind()` gives a portable `ErrorKind` to match on:

```rust
match File::open(path) {
    Ok(f) => use_it(f),
    Err(e) if e.kind() == io::ErrorKind::NotFound => create_it(path),
    Err(e) => return Err(e),
}
```

The kinds you will meet in this course: `NotFound` (a path in a directory that does not exist), `AlreadyExists` (`create_new`), `PermissionDenied`, `Interrupted` (retry), `UnexpectedEof` (`read_exact` hit the end), `InvalidInput`, `WouldBlock`.

## The `?` operator

`expr?` means: if this is `Ok(v)`, give me `v`; if it is `Err(e)`, **return `Err(e.into())` from the current function**. It is the error-handling you wrote by hand in C (`if (rc < 0) return rc;` after every call), as one character, with the conversion built in.

```rust
pub fn new(db_file: impl AsRef<Path>) -> io::Result<DiskManager> {
    let log = OpenOptions::new().read(true).append(true).create(true).open(&log_name)?;   // a missing directory returns here
    let db  = OpenOptions::new().read(true).write(true).create(true).truncate(false).open(&db_name)?;
    db.set_len(file_size_for(DEFAULT_DB_IO_SIZE))?;
    Ok(DiskManager { /* ... */ })
}
```

The `log` file is *open* when the second `?` returns; Rust closes it as the function unwinds (see the concept on ownership of files), where a C version has to remember an `fclose` on every error path.

```svg
caption: An Err travels up the call stack at every ?; each frame's locals (here the already-open log file) are dropped on the way. A panic unwinds the same way but is not caught by the callers' ?.
<svg viewBox="0 0 760 190" role="img" aria-label="Three nested calls; an error from open is returned through new to the caller, closing the log file on the way">
<defs><marker id="ie-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--bad)"/></marker></defs>
<rect class="box" x="20" y="30" width="170" height="52" rx="4"/><text class="mid fg" x="105" y="52">caller</text><text class="mid dim sm" x="105" y="70">decides what to do</text>
<rect class="box" x="250" y="30" width="200" height="52" rx="4"/><text class="mid fg" x="350" y="52">DiskManager::new</text><text class="mid dim sm" x="350" y="70">log is open, db is not</text>
<rect class="bad" x="510" y="30" width="230" height="52" rx="4"/><text class="mid fg" x="625" y="52">open(db)</text><text class="mid t-r sm" x="625" y="70">Err(NotFound)</text>
<path class="ln" d="M190 56 H248" marker-end="url(#ie-a)" style="stroke:var(--dim)"/>
<path class="ln" d="M450 56 H508" marker-end="url(#ie-a)" style="stroke:var(--dim)"/>
<path class="ln-w" d="M625 84 V118 H350 V84"/><path class="ln-w" d="M350 118 H105 V86" marker-end="url(#ie-a)"/>
<text class="t-w sm" x="480" y="112">? returns the error</text>
<text class="t-w sm" x="150" y="112">? returns it again</text>
<rect class="free" x="250" y="140" width="200" height="30" rx="4"/><text class="mid t-w sm" x="350" y="160">log file dropped: fd closed</text>
<line class="ln dash" x1="350" y1="84" x2="350" y2="140" style="stroke:var(--warn)"/>
</svg>
```

## Err or panic?

The standard-library convention, and BusTub's: **an `Err` is for things the environment can do to a correct program** (the file is missing, the disk is full); **a panic is for a bug in the program** (an index out of range, a violated precondition, a broken invariant). BusTub writes the second kind as `BUSTUB_ASSERT`; Rust writes it as `assert!`, `unreachable!` or an out-of-range index.

| situation | which | because |
|---|---|---|
| `DiskManager::new` on a path in a missing directory | `Err(NotFound)` | the caller can recover (create the directory) |
| `write_page(PageId::INVALID, ...)` | panic | the caller is broken: no valid program does this |
| writing page 100 on a 4-page memory disk | panic | a caller-visible contract: the tests expect `ran out of disk space` |
| `read_at` returned `Interrupted` | retry, never surface | it says nothing about the file |
| `mutex.lock()` returned a poison error | `unwrap()` and panic | another thread already panicked; the data may be half-updated |

> [!WHY] Why not just `unwrap()` everywhere?
> `unwrap()` turns an `Err` into a panic, which is right for a test and for "this cannot fail" (say it in a comment). In library code it hides a decision: you have decided, on behalf of every caller, that this failure is a bug. The disk manager returns `io::Result` so that the buffer pool above it can decide.
