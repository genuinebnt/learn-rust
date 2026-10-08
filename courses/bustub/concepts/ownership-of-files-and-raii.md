---
title: Who closes the file? Ownership, Drop and RAII
summary: A File owns its descriptor and closes it when dropped; moves replace C's double-close and leaked-fd bugs, and the drop order of fields decides what shuts down first.
minutes: 8
---
A file descriptor is a resource the operating system lends you until you give it back. C makes returning it your job; C++ and Rust make it the language's. This page is the difference, because the disk manager owns two files for its whole life and a scheduler later owns threads the same way.

## C: you pair every open with a close

```c
int fd = open(path, O_RDWR | O_CREAT, 0644);
if (fd < 0) return -1;
if (ftruncate(fd, size) < 0) { close(fd); return -1; }   // forget this and the descriptor leaks
...
close(fd);                                                // forget this on any path and it leaks; do it twice and you close someone else's fd
```

Every early return needs the `close`. A descriptor is just an `int`, so nothing stops you using it after closing it, or closing it twice; the number may by then belong to a different file.

## C++: RAII, but copies are a question

`std::fstream` closes in its destructor, so leaving the scope closes the file on every path, exceptions included. That is **RAII** (resource acquisition is initialisation): a resource's lifetime is tied to an object's. Streams are movable but not copyable, because two owners would mean two closes.

## Rust: `File` owns its descriptor; Drop closes it

`std::fs::File` is a struct holding the descriptor. When it goes out of scope, its `Drop` implementation calls `close`. Because Rust values have exactly one owner, the language proves there is exactly one close:

```rust
let log = OpenOptions::new().append(true).create(true).open(&log_name)?;
let db  = OpenOptions::new().read(true).write(true).open(&db_name)?;   // if this returns Err, `log` is dropped: closed
let manager = DiskManager { log_io: Mutex::new(log), db_io: Mutex::new(DbIo { file: db, /* .. */ }), /* .. */ };
// `log` and `db` were moved into the struct: they cannot be used or closed from here any more
```

A **move** transfers ownership. After `let b = a;` the name `a` is unusable (a compile error), which is how Rust rules out both the use-after-close and the double close. To get a second handle to the same open file you must ask: `file.try_clone()` duplicates the descriptor (`dup`), and each clone closes its own.

```svg
caption: The disk manager owns the Mutexes, which own the files, which own the descriptors. Dropping the DiskManager drops everything below it, in declaration order; nothing is closed twice and nothing is forgotten.
<svg viewBox="0 0 760 230" role="img" aria-label="An ownership tree from DiskManager through two Mutex fields to two File values and their file descriptors">
<rect class="hot" x="20" y="20" width="170" height="44" rx="4"/><text class="mid fg" x="105" y="47">DiskManager</text>
<rect class="box" x="270" y="20" width="200" height="40" rx="4"/><text class="mid fg" x="370" y="45">db_io: Mutex&lt;DbIo&gt;</text>
<rect class="box" x="270" y="132" width="200" height="40" rx="4"/><text class="mid fg" x="370" y="157">log_io: Mutex&lt;File&gt;</text>
<rect class="blue" x="540" y="20" width="200" height="40" rx="4"/><text class="mid t-b" x="640" y="45">File (db)  &#8594; fd 3</text>
<rect class="blue" x="540" y="132" width="200" height="40" rx="4"/><text class="mid t-b" x="640" y="157">File (log)  &#8594; fd 4</text>
<path class="ln" d="M190 42 H268"/><path class="ln" d="M105 64 V152 H268"/>
<path class="ln" d="M470 40 H538"/><path class="ln" d="M470 152 H538"/>
<text class="t-w sm" x="285" y="86">1. dropped first</text><text class="t-w sm" x="285" y="198">2. dropped second</text>
<text class="dim sm" x="540" y="86">close(3)</text><text class="dim sm" x="540" y="198">close(4)</text>
<text class="dim sm" x="20" y="222">fields drop in declaration order; each owner has exactly one</text>
</svg>
```

## Drop order

When a struct is dropped, its fields are dropped in **declaration order**, after the struct's own `Drop::drop` (if it has one) ran. For `DiskManager { db_file_name, log_file_name, db_io, log_io, ... }` that means the db file closes before the log. In C++ members are destroyed in the *reverse* of declaration order. If one field must outlive another (a thread that borrows a queue, say), declaration order is how you say so, and it is a very easy thing to get backwards when porting.

## What Drop does not do

- **It cannot report errors.** `close` can fail (a deferred write error on some file systems), but `Drop::drop` returns nothing, so the error is discarded. If you need to *know* the data reached the disk, call `file.sync_all()?` yourself first; that is what `DiskManager::shut_down` does.
- **It does not flush a `BufWriter`'s mistakes away.** A `BufWriter` flushes on drop, also ignoring errors. `File` has no user-space buffer, so there is nothing to flush.
- **It does not run if you leak** (`mem::forget`, a reference cycle, a `std::process::exit`). Leaking is safe in Rust, just wasteful.

## Sharing an open file between threads

`File`'s read and write methods that take an offset (`read_at`, `write_at`) take `&self`, and `File` is `Sync`, so any number of threads can use one `File` through a shared reference without a lock *for the file itself*. What needs a lock is **your bookkeeping** about it (the page table), which is why the disk manager puts the file and its page table in one `Mutex`: see the concept on `Mutex`.

> [!PORT] The porting rule
> A C++ class that owns a handle (`fstream`, a `unique_ptr`, a thread) becomes a Rust struct whose fields own the same things, with no destructor written by hand. If you find yourself wanting to write `impl Drop`, ask whether a field already does it: you need your own `Drop` only for cleanup the fields cannot do (stopping a worker thread, say), which is exactly the disk scheduler's job in module 1b.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `File::open(p)` / `File::create(p)` | read-only / write, truncating | quick scripts |
| `OpenOptions::new().read(true).write(true).create(true).truncate(false).open(p)` | exactly the flags you want | databases |
| `.append(true)` | every write goes to the end, chosen by the OS | logs |
| `f.set_len(n)` / `f.metadata()?.len()` | resize / size | pre-allocating, checking |
| `f.sync_all()` / `f.sync_data()` | make the data durable (`fsync`) | commit points |
| `f.try_clone()` | a second handle to the same open file (`dup`) | sharing a descriptor |
| `drop(f)` / end of scope | closes the descriptor | automatic |
| `std::mem::replace(&mut self.f, new)` | swap in a replacement | reopening |

```rust test
use std::fs::OpenOptions;
use std::io::{Read, Write};

#[test]
fn append_and_reopen_without_truncating() {
    let path = std::env::temp_dir().join("anneal-raii-1.log");
    let _ = std::fs::remove_file(&path);
    {
        let mut log = OpenOptions::new().append(true).create(true).open(&path).unwrap();
        log.write_all(b"abc").unwrap();
    }                                                          // `log` dropped: the descriptor is closed here
    {
        let mut log = OpenOptions::new().append(true).create(true).open(&path).unwrap();    // create(true) on an existing file keeps it
        log.write_all(b"def").unwrap();
    }
    let mut s = String::new();
    std::fs::File::open(&path).unwrap().read_to_string(&mut s).unwrap();
    assert_eq!(s, "abcdef");
}
```

```rust test
use std::fs::{File, OpenOptions};
use std::io;
use std::path::Path;

struct Db { data: File, log: File }

fn open_db(dir: &Path) -> io::Result<Db> {
    let log = OpenOptions::new().append(true).create(true).open(dir.join("db.log"))?;
    // If the next line fails, `log` is dropped on the way out: no cleanup code, no leaked descriptor.
    let data = OpenOptions::new().read(true).write(true).create(true).truncate(false).open(dir.join("db.data"))?;
    data.set_len(8192 * 17)?;
    Ok(Db { data, log })
}

#[test]
fn a_failed_second_open_closes_the_first() {
    let dir = std::env::temp_dir().join("anneal-raii-2");
    std::fs::create_dir_all(&dir).unwrap();
    let db = open_db(&dir).unwrap();
    assert_eq!(db.data.metadata().unwrap().len(), 8192 * 17);
    assert!(open_db(&dir.join("no/such/dir")).is_err());
}
```

### In the exercises

- **1a-01 Part 3:** `DiskManager::new` is `open_db` with the course's names: log first with `append`, then the db file with `read`, `write`, `create` and **`truncate(false)`**, then `set_len(file_size_for(16))`. The "existing database keeps its bytes" test is the one that fails if you forget `truncate(false)`.
- **1a-05:** `write_log` appends through the `Mutex<File>`; reopening must keep old records.
- **1a-08 (boss):** `shut_down` calls `sync_all()` on both files: the one place the course makes data durable.

### Where it is used

- **Everything that holds an OS resource**: sockets, mutex guards, temp files (`tempfile` deletes on drop), database connections returned to a pool on drop.
- **Write-ahead logs**: opened append-only, flushed with `sync_data` at commit.
- **Defensive programming**: because ownership is single, "use after close" and "double close" are compile errors, not CVEs.
