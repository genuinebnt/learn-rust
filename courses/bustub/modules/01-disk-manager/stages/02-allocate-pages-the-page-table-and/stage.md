Pages have ids; the file has slots. This stage is the mapping between the two and the bookkeeping that keeps it honest: a **page table** (page id → slot), a **free list** for the slots of deleted pages, an **allocator** that grows the file by doubling, and the three operations built on them: `write_page`, `read_page` and `delete_page`, all behind one latch.

It is the first stage with an invariant to protect rather than a function to compute. A slot is either in the page table or on the free list, never both and never neither, and three different methods change that. The hints below are about holding that invariant while threads write concurrently.

> [!TIP] Check the invariant in debug builds
> Write a private `fn check(&self)` that asserts every slot below `num_slots` is in exactly one of `pages` or `free_slots`, and call it under `debug_assert!` at the end of every method that changes either. A leaked slot never fails a plain test; this finds it the moment it happens.

Work through the parts in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Hand out fresh slots

**Where this fits.** A new page needs a place to live. The allocator decides which slot.

### The task

`DbIo` (given, in `src/storage/disk/disk_manager.rs`) is everything the db file's lock protects: the file, the page table, the free list and two counters. The disk manager keeps it in a `Mutex<DbIo>`, so one thread at a time touches any of it.

Implement the first part of `DbIo::allocate_slot`: always take a fresh slot at the end. `num_slots` counts how many have been handed out, so the next fresh slot **is** `num_slots`; hand it out and move the counter on. (Stages 11 and 12 add growing the file and reusing freed slots to this same function.) `DiskManager::allocate_slot` is given: it takes the lock and calls yours.

### Tests

- The first slot is `0`; slots then count up with no gaps and no repeats.
- Four threads allocating 25 slots each get exactly `0..100` between them.

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

- Pages 1000 then 3 get slots 0 then 1 (ids needn't be dense): `slot_of` says so.
- Rewriting a page keeps its slot; the next fresh slot is still the next one.
- Each page's bytes are in the file at its slot's offset.
- `PageId::INVALID` panics (given code).

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

- A page reads back what was written; ten pages don't interfere with each other.
- A page never written reads as zeros, even into a buffer full of `0xFF`.
- Reading five unknown pages allocates nothing: the next fresh slot is still `0`.

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

## Part 4 · Grow the file by doubling

**Where this fits.** The file started with room for 16 pages. What happens at the 17th?

### The task

`page_capacity` is how many pages the file has room for; the file's length is always `file_size_for(page_capacity)`. In `DbIo::allocate_slot` (`src/storage/disk/disk_manager.rs`), after the fresh slot is chosen: if the slot **doesn't fit** (`slot >= page_capacity`), **double** `page_capacity` and `set_len` the file to the new size.

### Tests

- 16 allocations leave the file at 17 pages; the 17th (slot 16) makes it 33; then 65, then 129.
- 100 pages written leave a file of exactly 129 pages.
- After every allocation from 1 to 200, the size is `(next_power_of_two(max(n, 16)) + 1)` pages. Pages written before a growth still read back after it.

### Syntax and methods

```rust
self.page_capacity *= 2;
self.file.set_len(file_size_for(self.page_capacity))?;
```

### Notes

Why double instead of adding a page each time? Resizing is a system call that may have to move or reserve file blocks. Doubling makes a file of `n` pages resize only `O(log n)` times, so growth is cheap **on average**: the same amortised argument as `Vec::push`.

### In BusTub

```cpp
if (pages_.size() + 1 >= page_capacity_) {
    page_capacity_ *= 2;
    std::filesystem::resize_file(db_file_name_, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
}
```

### The C/C++ way
| C / C++ | Rust |
|---|---|
| C: `buf = realloc(buf, new_cap)` (may move; old pointers dangle) | `Vec` grows itself; indexes survive, references don't (the borrow checker enforces it) |
| `std::vector::push_back` grows by 1.5x (MSVC) or 2x (libstdc++, libc++) | `Vec` doubles (amortised O(1)); `Vec::reserve` / `with_capacity` to plan ahead |
| `std::filesystem::resize_file(path, n)`, `ftruncate(fd, n)` | `file.set_len(n)` |
| growth factor 2 wastes up to half the file; 1.5 reuses freed blocks better in allocators | file growth is a design choice either way; BusTub doubles |

**Pitfall in C:** after `realloc`, every pointer into the old block is dangling. The same shape of bug in a buffer pool (a pointer to a frame kept across a resize) is why frames here will be indexed, not pointed to.

### Learn more
- [`Vec` capacity and growth](https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation)
- CMU 15-445 lecture "Database Storage I": how the file is organised into pages

## Part 5 · delete_page and the free list

**Where this fits.** Pages get deleted. Their slots must not be lost, or the file grows forever.

### The task

In `src/storage/disk/disk_manager.rs`:
- `delete_page(page_id)`: remove the page from the page table and push its slot onto `free_slots`. If the page isn't there, do nothing (and free nothing).
- `DbIo::allocate_slot`: *before* anything else, try to reuse a freed slot (`free_slots.pop()`).

`free_slots` is used as a **stack**: the most recently freed slot is reused first.

### Tests

- A deleted page reads as zeros again, and has no slot.
- Delete pages 1 (slot 0) and 3 (slot 2); the next two new pages get slot 2, then slot 0, and only then a fresh slot.
- Deleting an unknown page, or the same page twice, frees at most one slot (a slot freed twice would be given to two pages).
- Writing 40 pages, deleting them all, and writing 40 others leaves the file size unchanged.

### Syntax and methods

```rust
let Some(slot) = io.pages.remove(&id) else { return; };   // let-else: bail out when remove() gives None
io.free_slots.push(slot);                                   // Vec as a stack
if let Some(slot) = self.free_slots.pop() { return Ok(slot); }
```

### Notes

The file never shrinks, it only stops growing; real systems return the space or reorganise (vacuum / compaction). This is why a freed page that is later read must come back as zeros, even though its old bytes are still in the slot until reused: `read_page` goes through the page table, and the deleted page isn't in it.

### In BusTub

```cpp
void DiskManager::DeletePage(page_id_t page_id) {
  std::scoped_lock scoped_db_io_latch(db_io_latch_);
  if (pages_.find(page_id) == pages_.end()) { return; }
  size_t offset = pages_[page_id];
  free_slots_.push_back(offset);
  pages_.erase(page_id);
  num_deletes_ += 1;
}
```

### The C/C++ way
| C++ | Rust |
|---|---|
| `v.push_back(x)` / `v.pop_back()` | `v.push(x)` / `v.pop()` → `Option<T>` |
| `v.back()` on an **empty** vector is undefined behaviour; `if (!v.empty()) { x = v.back(); v.pop_back(); }` | `if let Some(x) = v.pop()`: emptiness is a value you must handle |
| `m.erase(k)` returns how many were erased (0 or 1) | `m.remove(&k)` returns `Option<V>`: the removed value, so you get the slot back in one step |
| `if (m.find(k) == m.end()) return;` early exit | `let Some(slot) = m.remove(&k) else { return };` |
| a "free list" threaded through the freed objects themselves (C: `struct free_block { struct free_block *next; }`) | safe Rust keeps a `Vec<usize>` of indices; an intrusive list is a later module |

**Pitfall in the C++:** double free. Deleting a page twice pushes its slot twice, and two pages then share a slot. The `Option` from `remove` makes the second delete a no-op by construction.

### Learn more
- [`HashMap::remove`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.remove) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Hints

### Name the invariant, then check it after every method

Every slot below `num_slots` is either a value in `pages` or an element of `free_slots`: not both, not neither. `write_page` (new id), `delete_page` and `allocate_slot` are the only code that moves slots between those places. Write each as "take a slot from here, put it there" and re-check the invariant at the end. A leaked slot (in neither place) never fails a test; it just makes the file grow forever.

### One critical section per decision

"Do I already have a slot for this page id?" and "if not, give it one" must happen under the same lock acquisition, or two threads writing the same new page get two slots and one of them leaks. That is why the file, the page table and the free list sit in one struct behind one `Mutex` rather than three locks: with a single lock there is no lock ordering to get wrong. BusTub calls it `db_io_latch_`.

### Deleted pages and zeros

After `delete_page`, `read_page` of that id must give zeros. You do not have to write zeros into the freed slot: the page table entry is gone, so the answer is structural. Think about when that would not be acceptable (a slot that held sensitive data is still on disk) and what the next owner of the slot sees if it only partially overwrites it. Also decide whether freed slots are reused newest-first or oldest-first; both pass, and one of them keeps the file denser at the front.

### Growing the file: what does an error leave behind?

When the fresh slot would not fit, double `page_capacity` and `set_len` the file. Doubling makes growth amortised O(1) instead of one syscall per page, and an explicit `set_len` keeps `get_db_file_size` predictable instead of letting a write past the end extend the file as a side effect. The subtle part is the order of the two updates: if `set_len` fails after you have bumped the counters, the structure claims room the file does not have. Pick an order, and make sure an I/O error leaves a state you can describe.
