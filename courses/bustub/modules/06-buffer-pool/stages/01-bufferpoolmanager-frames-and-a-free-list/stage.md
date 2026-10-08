This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · BufferPoolManager: frames and a free list

**Where this fits.** The disk is big and slow; memory is small and fast. The **buffer pool** is the database's own page cache: a fixed number of in-memory **frames**, each able to hold one 8 KiB page. Everything above it (indexes, tables) reads and writes pages *through* the pool and never touches the disk.

### The idea

- A **frame** is a slot in memory. A **page** lives in a frame while it is "resident".
- The **page table** maps a resident page id to its frame.
- **Free frames** hold no page.
- A **pin count** per frame says how many users are using the page right now. A pinned page can't be evicted.
- The **replacer** (your `ArcReplacer`) picks the victim among unpinned pages when no frame is free.
- A **dirty** flag says the bytes differ from the disk, so the page must be written back before its frame is reused.

### The task

`BufferPoolManager` (`src/buffer/buffer_pool_manager.rs`) has its parts declared: `frames` (each `RwLock<Box<PageData>>`: the bytes behind a reader-writer latch), an `Inner` behind a `Mutex` (page table, free list, per-frame metadata, replacer, next page id: BusTub's `bpm_latch_`) and a `DiskScheduler` from module 1b. The layout is a suggestion; the tests use only the public methods. Implement `new(num_frames, disk)` (all frames zeroed and free, empty page table, a replacer for `num_frames` frames, a scheduler on the disk) and `size()`.

### Tests

- `size()` is the number of frames (also 1 and 0). Every frame starts as 8192 zero bytes.

### Syntax and methods

```rust
let frames = (0..num_frames).map(|_| RwLock::new(Box::new([0u8; BUSTUB_PAGE_SIZE]))).collect();   // Vec<RwLock<Box<PageData>>>
(0..num_frames).rev().map(FrameId).collect::<Vec<_>>()   // a tuple-struct constructor is a function: FrameId(3)
DiskScheduler::new(disk)                                  // disk: Arc<dyn DiskIo>
```

### Notes

**One lock for the bookkeeping, one latch per frame.** `Mutex<Inner>` protects the *metadata* (who is where, pin counts): it is held briefly. The frame's `RwLock` protects the *bytes*: users hold it while they read or write the page, which can be long. Keeping those two apart is the central design point of every buffer pool (stage "Deadlock" in the next module shows what happens when they are mixed up).

BusTub allocates each frame separately (`std::vector<char>`) rather than as one big array, deliberately so that AddressSanitizer catches overruns; here each frame is its own `Box<[u8; 8192]>` and a slice index overrun panics.

### In BusTub

```cpp
BufferPoolManager::BufferPoolManager(size_t num_frames, DiskManager *disk_manager, LogManager *log_manager)
    : num_frames_(num_frames), next_page_id_(0), bpm_latch_(std::make_shared<std::mutex>()),
      replacer_(std::make_shared<ArcReplacer>(num_frames)), disk_scheduler_(std::make_unique<DiskScheduler>(disk_manager)),
      log_manager_(log_manager) {
  next_page_id_.store(0);
  frames_.reserve(num_frames_);  page_table_.reserve(num_frames_);
  for (size_t i = 0; i < num_frames_; i++) { frames_.push_back(std::make_shared<FrameHeader>(i)); free_frames_.push_back(static_cast<int>(i)); }
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<std::mutex> bpm_latch_` (shared so page guards can lock it) | `Mutex<Inner>` inside the struct; guards borrow the pool (`&BufferPoolManager`) |
| `std::vector<std::shared_ptr<FrameHeader>>` | `Vec<RwLock<Box<PageData>>>`: no reference counting needed, frames never move |
| `std::list<frame_id_t> free_frames_` | `Vec<FrameId>` used as a stack |
| `frames_.reserve(n)` | `Vec::with_capacity(n)`, or `collect()` from an iterator of known length |
| `BusTub: char data_[PAGE_SIZE]` accessed through `Page::GetData()` returning `char *` | `RwLock<Box<[u8; N]>>`: access only through a lock guard |

**Port rule:** a C++ class holding `std::mutex` plus a bag of members the mutex "protects" becomes a struct holding `Mutex<Inner>` with those members in `Inner`; the data that needs a *different* lock (the page bytes) stays outside it.

### Learn more
- Hellerstein, Stonebraker, Hamilton, [*Architecture of a Database System*](https://www.nowpublishers.com/article/Details/DBS-002), §5.3 (buffer management) · *The Internals of PostgreSQL*, [Buffer Manager](https://www.interdb.jp/pg/pgsql08.html)
- CMU 15-445 "Memory Management" lecture (linked below) · [`RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html) · [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html)

## Part 2 · new_page: hand out page ids

**Where this fits.** Pages need names before they exist.

### The task

Implement `new_page()` in `src/buffer/buffer_pool_manager.rs`: return a fresh `PageId`: 0, then 1, 2, ... No two callers, even concurrent ones, may get the same id. It touches neither memory nor disk: the page comes into existence when it is first fetched (and reads as zeros, because the disk has never seen it).

### Tests

- Ids count up from 0; `new_page` does no disk I/O; 4 threads × 50 calls get 200 distinct ids `0..200`.

### Syntax and methods

```rust
let mut inner = self.inner.lock().unwrap();
let id = PageId(inner.next_page_id);
inner.next_page_id += 1;
```

(An `AtomicI32::fetch_add(1, Relaxed)` would also do, without taking the pool's lock: BusTub's `std::atomic<page_id_t> next_page_id_`.)

### Notes

Where a counter lives decides how it is protected: inside the `Mutex<Inner>` it is protected for free; as an `AtomicI32` it is lock-free. Both are correct; the atomic avoids contention on the pool lock, the mutex keeps *all* state under one lock (simpler to reason about). Pick one and keep it. Page ids are never reused here, even after `delete_page`; real systems recycle them.

### In BusTub

```cpp
auto BufferPoolManager::NewPage() -> page_id_t { /* TODO(P1): Add implementation */ }   // allocates the next id; the page is brought in lazily
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::atomic<page_id_t> next_page_id_; next_page_id_++` (`fetch_add` with `seq_cst`) | `AtomicI32::fetch_add(1, Ordering::Relaxed)` |
| `page_id_t` = `int32_t`, overflows after 2^31 pages (16 TiB at 8 KiB) with undefined behaviour for signed overflow | `i32` overflow panics in debug, wraps in release; use `i64`/`u64` for a real system |
| returning the id through an out-parameter (`NewPage(&page_id)`) in older BusTub | returning it |

### Learn more
- [`AtomicI32`](https://doc.rust-lang.org/std/sync/atomic/type.AtomicI32.html) · *Rust Atomics and Locks*, [chapter 2: atomics](https://marabos.nl/atomics/atomics.html)
