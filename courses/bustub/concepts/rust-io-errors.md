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

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `io::Result<T>` = `Result<T, io::Error>` | the return type of anything that touches the OS | every I/O function |
| `expr?` | return the `Err` early (and convert it with `From`) | propagating |
| `e.kind()` → `ErrorKind::{NotFound, PermissionDenied, Interrupted, UnexpectedEof, ..}` | what happened, portably | deciding to retry or recover |
| `e.raw_os_error()` | the `errno` number | logging |
| `io::Error::new(kind, "msg")` / `io::Error::other("msg")` | make your own | wrapping a failure |
| `result.map_err(\|e\| ..)` / `.ok_or(..)` / `.ok_or_else(..)` | change an error, or turn an `Option` into a `Result` | adapting |
| `result.unwrap_or_else(\|e\| ..)` / `.unwrap_or_default()` | a fallback value | when you can continue |

```rust test
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::Path;

fn read_config(path: &Path) -> io::Result<String> {
    let mut s = String::new();
    File::open(path)?.read_to_string(&mut s)?;                // two fallible steps, one `?` each
    Ok(s)
}

fn read_or_default(path: &Path) -> io::Result<String> {
    match read_config(path) {
        Ok(s) => Ok(s),
        Err(e) if e.kind() == io::ErrorKind::NotFound => Ok(String::from("defaults")),     // an expected failure: recover
        Err(e) => Err(e),                                      // anything else is not ours to hide
    }
}

#[test]
fn recover_from_not_found_only() {
    let dir = std::env::temp_dir().join("anneal-io-errors-1");
    fs::create_dir_all(&dir).unwrap();
    let missing = dir.join("nope.conf");
    assert_eq!(read_or_default(&missing).unwrap(), "defaults");

    let real = dir.join("real.conf");
    fs::write(&real, "x=1").unwrap();
    assert_eq!(read_or_default(&real).unwrap(), "x=1");

    let err = read_or_default(&dir).unwrap_err();             // a directory is not a file: a different kind, so it propagates
    assert_ne!(err.kind(), io::ErrorKind::NotFound);
}
```

```rust test
use std::io;

#[derive(Debug)]
enum DbError { Io(io::Error), BadPage(u32) }

impl From<io::Error> for DbError {
    fn from(e: io::Error) -> Self { DbError::Io(e) }          // this is what `?` uses to convert
}

fn read_page(id: u32) -> Result<[u8; 4], DbError> {
    if id > 100 { return Err(DbError::BadPage(id)); }
    let bytes = std::fs::read("/definitely/not/here")?;       // io::Error becomes DbError::Io through From
    Ok(bytes.try_into().unwrap_or([0; 4]))
}

#[test]
fn your_own_error_type_and_question_mark() {
    assert!(matches!(read_page(500), Err(DbError::BadPage(500))));
    assert!(matches!(read_page(1), Err(DbError::Io(_))));
    let e = io::Error::other("the disk panicked");
    assert_eq!(e.kind(), io::ErrorKind::Other);
    assert_eq!(e.to_string(), "the disk panicked");
}
```

### In the exercises

- **1a-01 (`DiskManager::new`):** open the log, then the db file, with `?` (the `read_config` shape). A test with a path in a missing directory expects `Err`, not a panic.
- **1a-01 to 1a-03:** if you read in a loop, retry `ErrorKind::Interrupted` and return every other error: `Err(e) if e.kind() == io::ErrorKind::Interrupted => continue`.
- **1b-02:** a failing disk's `io::Error` travels back through the promise (`DiskResult = io::Result<Box<PageData>>`); the panicking-disk case uses `io::Error::other("the disk panicked")`.

### Where it is used

- **Every program that touches files, sockets or processes**: the `io::Error` kind decides between retry (`Interrupted`, `WouldBlock`), recover (`NotFound`) and give up.
- **Library error types**: `thiserror`/`anyhow` (and your own `enum` with `From<io::Error>`, the second example) are conveniences over the same `?` mechanism.
- **Databases**: a failed `write` or `fsync` is the most dangerous error there is (the data may not be durable); production engines treat it as fatal rather than retry, because the page cache state after a failed `fsync` is undefined (the "fsyncgate" episode in PostgreSQL).
