Observability, the log, and a seam. You add the lock-free counters the tests and benchmarks read, the log file's append-and-read-at-offset protocol (the recovery manager's future reader), and `DiskIo`: the trait that makes the real `DiskManager`, a fixed-size in-memory disk and an unbounded in-memory disk interchangeable for everything above them.

None of it is hard to type; the work is in the contracts. Count *when*, append *atomically*, and decide what each disk does when it is asked for something it cannot do.

> [!TIP] Watch the syscalls
> `strace -f -e trace=pwrite64,write,pread64 cargo test s1a_ …` (Linux) shows what each call really does: positional writes carry their offset, and the log's `write` carries no offset at all because `O_APPEND` chooses it. On macOS use `sudo fs_usage -w -f filesys <pid>`.

Work through the parts in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Count the I/O with atomics

**Where this fits.** Later modules assert how many writes happened ("the buffer pool wrote the dirty page exactly once"). The disk manager keeps the count.

### The task

Three counters (`num_writes`, `num_deletes`, `num_flushes`) live outside the mutex as `AtomicUsize`. In `src/storage/disk/disk_manager.rs`:
- count a write in `write_page` (every call, rewrites included) and a delete in `delete_page` (only when the page existed);
- fill in the getters `get_num_writes`, `get_num_deletes`, `get_num_flushes`. (Flushes are counted by the log, stage 14.)

### Tests

- All three start at 0. Two writes to page 0 and one to page 1 make 3 writes. Reads don't count.
- Of three `delete_page` calls (one real, one repeat, one unknown) only one counts.
- Eight threads writing 50 pages each make exactly 400.

### Syntax and methods

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let n = AtomicUsize::new(0);          // not `mut`: atomics change through &self
n.fetch_add(1, Ordering::Relaxed);    // one indivisible increment; returns the old value
n.load(Ordering::Relaxed)             // the current value
```

### Notes

Why not put the counters in `DbIo`? So that anyone can read them without the file lock, and so incrementing from many threads can never race. `Ordering::Relaxed` means "this number must be right, but I don't need it to order any other memory": exactly right for a statistic. (`Acquire`/`Release` come later, in the lock-free structures.)

### In BusTub

```cpp
num_writes_ += 1;                                           // a plain int, bumped under db_io_latch_
auto DiskManager::GetNumWrites() const -> int { return num_writes_; }   // read with no lock: a data race
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `int num_writes_; num_writes_ += 1;` from many threads: a **data race, undefined behaviour** | `AtomicUsize::fetch_add`, or increment under the mutex |
| `std::atomic<int> n; n.fetch_add(1);` defaults to `memory_order_seq_cst` (the strongest, slowest) | the ordering is always spelled out: `Ordering::Relaxed` for a statistic |
| C11 `<stdatomic.h>`: `atomic_fetch_add_explicit(&n, 1, memory_order_relaxed)` | same operation, same ordering names |
| `memory_order_relaxed / acquire / release / acq_rel / seq_cst` | `Ordering::Relaxed / Acquire / Release / AcqRel / SeqCst` (no `consume`) |
| a getter that reads a plain int without the lock (BusTub's `GetNumWrites`) | `load(Relaxed)`: a defined, race-free read |

**Port rule:** every shared counter that C++ wrote as a plain `int` and "protected by convention" is either `Atomic*` or inside the `Mutex`. Pick `Relaxed` only when the number does not order other memory.

### Learn more
- [`AtomicUsize`](https://doc.rust-lang.org/std/sync/atomic/type.AtomicUsize.html) · [`Ordering`](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)

## Part 2 · write_log: append to the log file

**Where this fits.** The disk manager has a second file: the **write-ahead log** (the Recovery module builds the real one). For now it is a byte stream you can append to.

### The task

Implement `write_log(data)` in `src/storage/disk/disk_manager.rs`: append `data` to the log file and count one flush; an empty `data` does nothing at all.

### Tests

- Two writes `abc` and `def` leave `abcdef` in `test.log`; the db file is untouched.
- Each non-empty write is one flush (5 writes, 5 flushes); an empty write is none.
- Opening the disk manager again keeps the old records and appends after them.

### Syntax and methods

```rust
use std::io::Write;
let mut log = self.log_io.lock().unwrap();   // `mut`: Write::write_all takes &mut self
log.write_all(data)?;                        // io::Result<()>
```

### Notes

The file was opened with `append(true)`, so each `write_all` lands at the end regardless of anything else. Appending is also the fastest way to write to a disk, which is why logs are append-only.

### In BusTub

```cpp
void DiskManager::WriteLog(char *log_data, int size) {
  if (size == 0) { return; }   // no effect on num_flushes_ if log buffer is empty
  num_flushes_ += 1;
  log_io_.write(log_data, size);   // sequence write
  log_io_.flush();                 // flushes the *stream's* buffer to the OS; not an fsync
}
```

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `open(.., O_WRONLY \| O_APPEND)`; `write(fd, buf, n)`: the kernel appends atomically for each call | `ofstream(path, ios::app)`; `write(buf, n); flush();` | `OpenOptions::new().append(true)`; `write_all(buf)` |
| `fflush(f)` pushes libc's buffer to the **OS** only | `stream.flush()` the same | `File` has no user-space buffer: `flush()` is a no-op; use `sync_all` for the disk |
| `fsync(fd)` / `fdatasync(fd)` to reach the device | `fsync` via the native handle | `file.sync_all()` / `file.sync_data()` |
| short writes: `write` can return less than `n`; loop | `write` sets `badbit` on failure | `write_all` loops for you |

**Port rule:** if the C++ calls `flush()` and the comment says "make it durable", the Rust translation is `sync_data`/`sync_all`, **not** `flush`. (BusTub's own `flush()` is not durable.)

### Learn more
- [`io::Write`](https://doc.rust-lang.org/std/io/trait.Write.html) · CMU 15-445 lecture "Database Logging"

## Part 3 · read_log: read from an offset

**Where this fits.** Recovery will read the log back from the start. This is the reader.

### The task

Implement `read_log(buf, offset)` in `src/storage/disk/disk_manager.rs` It reads `buf.len()` bytes of the log starting at byte `offset`:
- if `offset` is **at or past the end** of the log: return `Ok(false)` and leave `buf` untouched;
- otherwise return `Ok(true)`; whatever the log doesn't have (a read running off the end) is **zero-filled**.

### Tests

- A record reads back; `abc` + `def` read from offset 0 (6 bytes) and from offset 3 (`def`).
- An empty log, or an offset at/after the end, gives `false` and leaves the buffer as it was.
- `hi` read into 8 bytes gives `hi` then six zeros, and `true`.
- After reopening, old records are still readable.

### Syntax and methods

```rust
log.metadata()?.len()               // the log's current length: u64
let n = read_full_at(&log, buf, offset)?;   // you wrote this in stage 6
buf[n..].fill(0);
```

### In BusTub

```cpp
auto DiskManager::ReadLog(char *log_data, int size, int offset) -> bool {
  if (offset >= GetFileSize(log_file_name_)) { return false; }
  log_io_.seekp(offset);
  log_io_.read(log_data, size);
  int read_count = log_io_.gcount();
  if (read_count < size) { log_io_.clear(); memset(log_data + read_count, 0, size - read_count); }
  return true;
}
```

### The C/C++ way
| C (POSIX) | C++ | Rust |
|---|---|---|
| `fstat(fd, &st); st.st_size` or `lseek(fd, 0, SEEK_END)` | `GetFileSize(path)` (a `stat` call by name) | `file.metadata()?.len()` |
| `pread` + zero the missing tail with `memset` | `seekp(off); read(); gcount(); clear(); memset()` | `read_full_at` + `buf[n..].fill(0)` |
| returns `bool` for "no data" and logs I/O errors | `auto ReadLog(...) -> bool` | `io::Result<bool>`: an error is an `Err`, "nothing there" is `Ok(false)` |

**Pitfall in the C++:** `seekp` is the *put* position and `seekg` the *get* position; for an `fstream` they are linked, but for separate `ifstream`/`ofstream` objects they are not.
BusTub's `ReadLog` calls `seekp` and then reads: it works only because it is one `fstream`. Positional `read_at` has no such trap.

### Learn more
- [`File::metadata`](https://doc.rust-lang.org/std/fs/struct.File.html#method.metadata)

## Part 4 · A trait for disks: DiskIo

**Where this fits.** The buffer pool will use *a disk*, not specifically the file one: tests run on in-memory disks. In C++ that is a base class with `virtual` methods. In Rust, a trait.

### The task

`DiskIo` (given) lists what a disk can do: `read_page`, `write_page`, `delete_page`. In `src/storage/disk/disk_manager.rs`:
- implement `DiskIo for DiskManager`: three one-line methods that call the `DiskManager` methods you wrote;
- implement `copy_page(disk, from, to)`: read page `from` into a local buffer, write it as page `to`, through whatever disk was passed in.

### Tests

- A `DiskManager` used as `&dyn DiskIo` writes, reads and deletes for real (its counters move).
- `Arc<dyn DiskIo>` can be handed to four threads that each write a page.
- `copy_page` copies; copying a never-written page writes zeros; it does exactly one read and one write on a test double.

### Syntax and methods

```rust
impl DiskIo for DiskManager {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        DiskManager::read_page(self, page_id, buf)   // the inherent method, named by its path
    }
}
pub fn copy_page(disk: &dyn DiskIo, from: PageId, to: PageId) -> io::Result<()> { /* .. */ }
let mut buf = [0u8; BUSTUB_PAGE_SIZE];               // 8 KiB on the stack is fine
```

### Notes

A struct's own method (`inherent`) wins over a trait method of the same name, so `self.read_page(..)` inside the impl would call the inherent one anyway; writing `DiskManager::read_page(self, ..)` makes that explicit. `&dyn DiskIo` is a reference to *some* disk, chosen at run time (a vtable call). `trait DiskIo: Send + Sync` says every disk can be shared between threads, which `Arc<dyn DiskIo>` needs.

### In BusTub

```cpp
virtual void WritePage(page_id_t page_id, const char *page_data);   // DiskManager's virtual methods
virtual void ReadPage(page_id_t page_id, char *page_data);
virtual void DeletePage(page_id_t page_id);
class DiskManagerMemory : public DiskManager { /* overrides them */ };
```

### The C/C++ way
| C | C++ | Rust |
|---|---|---|
| a struct of function pointers: `struct file_ops { int (*read)(..); int (*write)(..); }` (the Linux VFS does this) | `class Base { virtual void ReadPage(..) = 0; };` + `class Derived : public Base` | `trait DiskIo { fn read_page(..); }` + `impl DiskIo for DiskManager` |
| call through the table: `ops->read(..)` | call through a `Base *` / `Base &` (vtable) | call through `&dyn DiskIo` / `Box<dyn DiskIo>` / `Arc<dyn DiskIo>` (vtable) |
| (none) | `template <class Disk>` compile-time polymorphism | generics: `fn f<D: DiskIo>(d: &D)` (monomorphised, no vtable) |
| (none) | `override`; a virtual destructor, or deleting through a base pointer is UB | `Drop` runs for the concrete type through `Box<dyn Trait>`: no virtual-destructor mistake exists |
| `std::unique_ptr<Base>` / `std::shared_ptr<Base>` | | `Box<dyn Trait>` / `Arc<dyn Trait>` |

**Port rule:** a C++ abstract base class with only pure virtuals is a trait. One with data members and non-virtual helpers is a struct plus a trait (or a generic).
`: Send + Sync` is what C++ leaves to documentation: "this may be used from many threads".

### Learn more
- The Rust Book: [defining shared behaviour with traits](https://doc.rust-lang.org/book/ch10-02-traits.html) and [trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html)

## Part 5 · DiskManagerMemory: a disk of fixed size

**Where this fits.** Tests want a disk with no files and no waiting. Two in-memory disks live in `src/storage/disk/disk_manager_memory.rs`; this is the first.

### The task

`DiskManagerMemory::new(capacity)` holds `capacity` pages in one byte buffer: page `n` is bytes `n * 8192 .. (n + 1) * 8192`. Implement `new`, `range` (the bounds check and the byte range of a page), `read_page` and `write_page` (which counts the write). Ids outside `0..capacity` **panic** with a message saying the disk ran out of space: that is a bug in the caller, not an I/O error. A fresh disk reads as zeros. `delete_page` is given (it does nothing).

### Tests

- Pages read back and don't overlap; a fresh disk is all zeros; the count of writes is right.
- Page `capacity`, page 100 on a 4-page disk, and `PageId(-1)` all panic with "ran out of disk space" (reads and writes).
- The disk works as `Arc<dyn DiskIo>`.

### Syntax and methods

```rust
vec![0u8; n]                                        // n zero bytes
assert!(cond, "page {} out of range", id);          // panics with the message when cond is false
let at: std::ops::Range<usize> = start..start + BUSTUB_PAGE_SIZE;
buf.copy_from_slice(&memory[at.clone()]);            // both sides must have the same length, or it panics
self.memory.lock().unwrap()[at].copy_from_slice(data);
```

### In BusTub

```cpp
BUSTUB_ASSERT(static_cast<size_t>(page_id) < page_capacity_, "Ran out of disk space for limited memory disk manager implementation");
size_t offset = static_cast<size_t>(page_id) * BUSTUB_PAGE_SIZE;
memcpy(memory_ + offset, page_data, BUSTUB_PAGE_SIZE);
```

BusTub's `ReadPage` doesn't check the bound at all (undefined behaviour). Here both do.

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `new char[n]` ... `delete[] p` (manual; BusTub's destructor does this) | `vec![0u8; n]`: freed by `Drop` |
| `malloc(n)` is uninitialised; `calloc(1, n)` is zeroed | `vec![0; n]` is always initialised: no "uninitialised read" bug class |
| `memcpy(dst + off, src, size)`: no bounds check; overlapping ranges are UB | `dst[a..b].copy_from_slice(src)`: panics on a length mismatch; `copy_within` for overlap (`memmove`) |
| `BUSTUB_ASSERT(cond, "msg")` (aborts in debug builds) | `assert!(cond, "msg {}", x)` (a panic; in every build unless you use `debug_assert!`) |
| `assert(x)` from `<assert.h>` vanishes with `-DNDEBUG` | `assert!` always runs; `debug_assert!` is the vanishing one |

**Pitfall in the C++:** `DiskManagerMemory::ReadPage` has no bounds check at all, so reading past the end is undefined behaviour. Rust slices make that a panic.

### Learn more
- [`copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · [`assert!`](https://doc.rust-lang.org/std/macro.assert.html) · [`Range`](https://doc.rust-lang.org/std/ops/struct.Range.html)

## Part 6 · DiskManagerUnlimitedMemory: pages on demand

**Where this fits.** Most of BusTub's tests use this disk: no capacity to choose, pages appear when first written.

### The task

Pages live in a `Vec<Option<Box<PageData>>>` indexed by page id; `None` means "never written". In `disk_manager_memory.rs`, `DiskManagerUnlimitedMemory`:
- `write_page`: grow the `Vec` to length `id + 1` (filled with `None`), create the page if it is `None`, copy the data in, count the write;
- `read_page`: copy the page out if it exists, otherwise zero the buffer. Reading never creates a page;
- `get_memory_usage`: the number of existing pages times `BUSTUB_PAGE_SIZE`.

### Tests

- Pages 0, 1, 500 and 5000 read back; a page never written, or in a gap below a written page, reads as zeros.
- Rewriting replaces the page. Memory usage counts only pages that exist: two pages written is `2 * 8192`, a rewrite or a read of a missing page doesn't change it.
- `copy_page` (stage 16) works on this disk too.
- Eight threads write 25 pages each; all 200 read back and `get_num_writes` is 200. `PageId::INVALID` panics.

### Syntax and methods

```rust
pages.resize_with(at + 1, || None);                  // grow, filling new slots with the closure's result
let page = pages[at].get_or_insert_with(|| Box::new([0u8; BUSTUB_PAGE_SIZE]));   // &mut Box<PageData>
page.copy_from_slice(data);                           // a Box<[u8; N]> derefs to the array
match pages.get(at) { Some(Some(page)) => buf.copy_from_slice(&**page), _ => buf.fill(0) }
pages.iter().filter(|p| p.is_some()).count()
```

### Notes

Why `Option<Box<..>>` and not `Option<PageData>`? A `PageData` is 8 KiB, so a `Vec` of them reserves 8 KiB for every id up to the highest written. `Option<Box<T>>` is **one pointer wide** (the null pointer means `None`, a "niche"), so empty ids cost 8 bytes.

### In BusTub

```cpp
if (page_id >= static_cast<int>(data_.size())) { data_.resize(page_id + 1); }
if (data_[page_id] == nullptr) { data_[page_id] = std::make_shared<ProtectedPage>(); }
memcpy(ptr->first.data(), page_data, BUSTUB_PAGE_SIZE);
```

BusTub's version also has a **latency simulator** (sleeping 1 ms per random access, 0.1 ms for nearby pages) so tests can see a buffer pool hide disk latency. It comes in with the buffer pool module.

### The C/C++ way
| C++ | Rust |
|---|---|
| `std::vector<std::shared_ptr<Page>> data_; data_.resize(n);` | `Vec<Option<Box<PageData>>>`; `resize_with(n, \|\| None)` |
| a null pointer means "no page": `if (data_[i] == nullptr)` | `None`; `Option<Box<T>>` is the same size as a pointer, and `None` *is* the null pointer |
| `std::make_shared<T>()` | `Box::new(..)` for sole ownership; `Arc::new(..)` only if it is really shared |
| `std::optional<T>` | `Option<T>` |
| `std::shared_mutex` per page (BusTub's `ProtectedPage`) | `RwLock<..>`: a later stage when pages are shared |
| `std::this_thread::get_id()` | `std::thread::current().id()` |

**Port rule:** `shared_ptr` is the *last* resort in Rust, not the default. Ask "who owns this?": one owner means `Box`, many means `Arc`. BusTub uses `shared_ptr` liberally because C++ has no other cheap way to say "keep this alive".

### Learn more
- [`Option::get_or_insert_with`](https://doc.rust-lang.org/std/option/enum.Option.html#method.get_or_insert_with) · [`Vec::resize_with`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.resize_with) · [niche optimisation](https://doc.rust-lang.org/std/option/index.html#representation)

## Hints

### Count when it succeeded, with the weakest ordering that is correct

`Ordering::Relaxed` is enough for statistics: no other memory is published through these counters. C++'s `std::atomic` defaults to sequential consistency, which is stronger than needed. The more important decision is *placement*: increment after the write succeeded, so a failing write does not inflate `get_num_writes`; and a `write_log` of zero bytes is not a flush at all.

### The log has two cursors that must not meet

The log is opened for append, so every write lands at the end of the file atomically whatever any reader is doing. Reads use explicit offsets and never move a cursor. `read_log` returns `false` at or past the end of the log (the recovery loop's termination condition) and `true` with a zero-padded tail when the log ends mid-buffer, so a caller must decode lengths from the data and never trust `buf.len()`.

### Why `&dyn DiskIo` and not a generic parameter

A `BufferPoolManager<D: DiskIo>` would monomorphise and push the disk type into every signature above it. BusTub uses virtual dispatch (`DiskManager` has virtual methods that the memory disks override), and the cost of one indirect call per page I/O is noise next to a syscall. That is why `copy_page` takes `&dyn DiskIo`: it has to work on all three disks. The trait is `Send + Sync` with `&self` methods because each implementation owns its own locking.

### An in-memory disk still has to say no

`DiskManagerMemory` has a fixed capacity: writing page `capacity` is the in-memory version of a full disk, and the tests expect a loud failure rather than a silent write somewhere else. The unlimited disk has the opposite contract: pages appear, zeroed, on first write, and a page never written reads as zeros. Decide what each stores (one flat buffer versus one allocation per page), and what `get_memory_usage` should count. It should not count pages that were never written.
