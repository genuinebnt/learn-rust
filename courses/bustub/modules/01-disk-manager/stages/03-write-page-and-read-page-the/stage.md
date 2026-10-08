Pages have ids; the file has slots. This stage is the mapping between the two and the allocator behind it: a page table (`PageId → slot`), fresh slots at the end of the file, and the first versions of `write_page` and `read_page`, which must stay correct when several threads call them. It is the first stage with an invariant to protect rather than a function to compute, and the concept article shows how to write the checker.

> [!TIP] Check the invariant in debug builds
> Write a private `fn check(&self)` that asserts every slot below `num_slots` is in exactly one of `pages` or `free_slots`, and call it under `debug_assert!` at the end of every method that changes either. A leaked slot never fails a plain test; this finds it the moment it happens.

## Part 1 · Hand out fresh slots

**Where this fits.** A new page needs a place to live. The allocator decides which slot.

### The task

`DbIo` (given, in `src/storage/disk/disk_manager.rs`) is everything the db file's lock protects: the file, the page table, the free list and two counters. The disk manager keeps it in a `Mutex<DbIo>`, so one thread at a time touches any of it.

Implement the first part of `DbIo::allocate_slot`: always take a fresh slot at the end. `num_slots` counts how many have been handed out, so the next fresh slot **is** `num_slots`; hand it out and move the counter on. (Stages 11 and 12 add growing the file and reusing freed slots to this same function.) `DiskManager::allocate_slot` is given: it takes the lock and calls yours.

### Tests

- Slots count up from 0 with no gaps or repeats, also when four threads allocate at once.

### Syntax and methods

```rust
let mut io = self.db_io.lock().unwrap();   // MutexGuard<DbIo>: derefs to DbIo; the lock is released when `io` is dropped
self.num_slots += 1;                       // inside `impl DbIo`, `self` is &mut DbIo
```

### Notes

`lock()` returns a `Result`: if a thread panicked while holding the lock it is *poisoned*, and `unwrap()` passes that panic on. The threads test only passes because the counter lives **inside** the mutex.

### In BusTub

```cpp
return pages_.size() * BUSTUB_PAGE_SIZE;   // derived from the page table's size; here it's an explicit counter
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `pthread_mutex_t m; pthread_mutex_lock(&m); ... pthread_mutex_unlock(&m);` | `let g = m.lock().unwrap();` unlocks when `g` goes out of scope |
| `std::mutex m; std::scoped_lock l(m);` / `std::lock_guard` | `Mutex<T>` + `MutexGuard<T>` |
| the mutex and the data it protects are separate members; "protects" is a comment | `Mutex<DbIo>` **owns** the data: no lock, no access |
| forget to unlock on an early `return` / exception (C), or lock the wrong mutex (C++) | not expressible: the guard unlocks in `Drop`; there is only one mutex to lock |
| `std::atomic<size_t> next{0}; next.fetch_add(1)` for a counter | an `AtomicUsize`, or a plain field inside the `Mutex` (this stage) |

**Port rule:** a C++ class with `mutex_` + several fields it guards becomes `Mutex<Inner>` with those fields in `Inner`. In BusTub this is `db_io_latch_` + `pages_` + `free_slots_` → `Mutex<DbIo>`.

### Learn more
- [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · The Rust Book: [shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html)

## Part 2 · write_page: the page table

**Where this fits.** Callers know pages by id (`PageId(1000)`); the file is slots. The page table connects them.

### The task

`DbIo::pages: HashMap<PageId, usize>` maps a page id to its slot. Implement `write_page(page_id, data)` in `src/storage/disk/disk_manager.rs` (the invalid-id check is given):

- if the page has a slot, overwrite that slot;
- otherwise get a fresh slot from `io.allocate_slot()`, **remember it in the page table**, then write.

### Tests

- Pages 1000 then 3 get slots 0 then 1; rewriting a page keeps its slot; each page's bytes sit at its slot's offset.

### Syntax and methods

```rust
io.pages.get(&id)               // Option<&usize>
io.pages.insert(id, slot);      // Option<usize>: the old value, if there was one
match io.pages.get(&id) {
    Some(&slot) => slot,        // `&slot` copies the usize out of the reference
    None => { /* you need io.allocate_slot()? here */ }
}
write_slot(&io.file, slot, data)?;
```

### Notes

**The borrow trap.** `io.pages.get(&id)` borrows `io.pages`; `io.allocate_slot()` needs `&mut io`. If the shared borrow is still alive in the `None` arm, the compiler refuses. Matching `Some(&slot)` copies the number out, so the borrow ends. If you hit E0502, copy first: `let found = io.pages.get(&id).copied();`.

### In BusTub

```cpp
if (pages_.find(page_id) != pages_.end()) { offset = pages_[page_id]; }   // exists: overwrite in place
else { offset = AllocatePage(); }                                           // new: take a slot
...
pages_[page_id] = offset;
```

### The C/C++ way
| C++ (`std::unordered_map`) | Rust (`HashMap`) |
|---|---|
| `m.find(k) != m.end()` | `m.contains_key(&k)` / `m.get(&k).is_some()` |
| `m[k]` **inserts a default value** if `k` is missing; `m.at(k)` throws | `m[&k]` panics if missing; `m.get(&k)` → `Option<&V>`; nothing is inserted unless you say so |
| `m[k] = v;` / `m.emplace(k, v)` / `m.insert({k, v})` | `m.insert(k, v)` returns the old value; `m.entry(k).or_insert(v)` |
| iterator invalidation: inserting while holding an iterator or reference is **undefined behaviour** | the borrow checker rejects it (the "borrow trap" in this stage's notes) |
| `size_t offset = pages_[page_id];` copies a value out | `let slot = *io.pages.get(&id)?` or `Some(&slot)`: copy out so the borrow ends |

**Pitfall in the C++:** `pages_[page_id]` on a missing key quietly creates an entry with offset `0`, a classic source of "phantom page 0" bugs.

### Learn more
- [`HashMap`](https://doc.rust-lang.org/std/collections/struct.HashMap.html) · [`Option::copied`](https://doc.rust-lang.org/std/option/enum.Option.html#method.copied)
- The Rust Book: [references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)

## Part 3 · read_page: unknown pages read as zeros

**Where this fits.** The other half of the page table. Now a page can make the round trip.

### The task

Implement `read_page(page_id, buf)` in `src/storage/disk/disk_manager.rs`: if the page has a slot, `read_slot` it into `buf`; if it has never been written, fill `buf` with zeros. Reading must **not** change anything (no slot is allocated).

### Tests

- A page reads back what was written; a page never written reads as zeros and allocates no slot.

### Syntax and methods

```rust
match io.pages.get(&page_id) {
    Some(&slot) => read_slot(&io.file, slot, buf),   // returns io::Result<()>
    None => { buf.fill(0); Ok(()) }
}
```

### In BusTub

```cpp
if (pages_.find(page_id) != pages_.end()) { offset = pages_[page_id]; }
else { offset = AllocatePage(); }       // BusTub allocates a slot even for a read of an unknown page!
```

One difference on purpose: this port's reads never allocate.

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `void ReadPage(page_id_t id, char *page_data)`: an out-parameter, size known only by convention | `read_page(&self, id: PageId, buf: &mut PageData)`: the type is `&mut [u8; 8192]` |
| `page_id_t` is `int32_t`; `INVALID_PAGE_ID = -1` is a magic value anyone can pass | `PageId(i32)` newtype; `PageId::INVALID` only for on-disk formats; `Option<PageId>` in memory |
| errors: ignored return codes, or logged and returned (`LOG_DEBUG("I/O error"); return;`) | `io::Result<()>`: the caller must handle or `?` it |
| `memset(page, 0, size)` | `buf.fill(0)` |

**Port rule:** an out-parameter pointer (`T *out`) becomes `&mut T` or, better, a return value (`-> T`); here the page buffer stays an out-parameter because the caller owns the 8 KiB.

### Learn more
- [`match`](https://doc.rust-lang.org/book/ch06-02-match.html) on `Option` · BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp) `ReadPage`

## Performance

`write_page` is one hash lookup (O(1) on average), possibly one allocation, and one `pwrite`, all while holding the single `db_io` latch. `read_page` of an unknown page makes no syscall: it fills the buffer with zeros.

The consequence to understand is that I/O is **serialised**: the latch is held across the `pwrite`, so two threads writing different pages take turns. That is BusTub's choice (`db_io_latch_`) and it is deliberate: the disk is the bottleneck, and the parallelism lives one layer up, in the disk scheduler (module 1b). Releasing the latch before the write would let the page table change under you; that trade is worth discussing, not making by accident.

**Measure it.** Write 10 000 pages from 1 thread and then from 4 threads: expect no speedup, because of the latch. Count how long the latch is held (`Instant` around the critical section) and compare it with the time the `pwrite` takes.

## Hints

### Name the invariant, then check it after every method

Every slot below `num_slots` is either a value in `pages` or an element of `free_slots`: not both, not neither. `write_page` (new id), `delete_page` and `allocate_slot` are the only code that moves slots between those places. Write each as "take a slot from here, put it there" and re-check the invariant at the end. A leaked slot (in neither place) never fails a test; it just makes the file grow forever.

### One critical section per decision

"Do I already have a slot for this page id?" and "if not, give it one" must happen under the same lock acquisition, or two threads writing the same new page get two slots and one of them leaks. That is why the file, the page table and the free list sit in one struct behind one `Mutex` rather than three locks: with a single lock there is no lock ordering to get wrong. BusTub calls it `db_io_latch_`.
