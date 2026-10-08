Slots come and go. `delete_page` returns a slot to a free list so that a later page reuses it, and the allocator doubles the file when a fresh slot would not fit. Both are small, and both are where a leak or a stale read hides: the hints are about the order of updates and about what an I/O error leaves behind.

## Part 1 · Grow the file by doubling

**Where this fits.** The file started with room for 16 pages. What happens at the 17th?

### The task

`page_capacity` is how many pages the file has room for; the file's length is always `file_size_for(page_capacity)`. In `DbIo::allocate_slot` (`src/storage/disk/disk_manager.rs`), after the fresh slot is chosen: if the slot **doesn't fit** (`slot >= page_capacity`), **double** `page_capacity` and `set_len` the file to the new size.

### Tests

- The file doubles when a fresh slot would not fit (17 pages, then 33, 65, 129) and earlier pages still read back after a growth.

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

## Part 2 · delete_page and the free list

**Where this fits.** Pages get deleted. Their slots must not be lost, or the file grows forever.

### The task

In `src/storage/disk/disk_manager.rs`:
- `delete_page(page_id)`: remove the page from the page table and push its slot onto `free_slots`. If the page isn't there, do nothing (and free nothing).
- `DbIo::allocate_slot`: *before* anything else, try to reuse a freed slot (`free_slots.pop()`).

`free_slots` is used as a **stack**: the most recently freed slot is reused first.

### Tests

- A deleted page reads as zeros and has no slot; its slot is reused newest first; deleting twice frees one slot; deleting 40 pages and writing 40 others leaves the file size unchanged.

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

## Performance

Growth by doubling is amortised O(1): allocating `n` pages from a capacity of 16 calls `set_len` about `log2(n/16)` times, against `n` times if you grew by one page. For 1 000 pages that is 6 growth calls (16 → 32 → … → 1024) plus the one in `new`. Because the file is sparse, a bigger file costs address space, not disk blocks. `delete_page` is a hash removal and a `Vec::push`: it never touches the file, so it is O(1) and cannot fail.

The price of the free list is that a deleted slot is not returned to the operating system: the file never shrinks. That is fine here and a real engine's problem later (compaction, `fallocate` hole punching).

**Measure it.** Count `ftruncate` calls while allocating 1 000 pages (`strace -c -e trace=ftruncate`, or a counter in a test): expect 7 including `new`'s. Delete every page and write the same number again and check the file size did not change.

## Hints

### Deleted pages and zeros

After `delete_page`, `read_page` of that id must give zeros. You do not have to write zeros into the freed slot: the page table entry is gone, so the answer is structural. Think about when that would not be acceptable (a slot that held sensitive data is still on disk) and what the next owner of the slot sees if it only partially overwrites it. Also decide whether freed slots are reused newest-first or oldest-first; both pass, and one of them keeps the file denser at the front.

### Growing the file: what does an error leave behind?

When the fresh slot would not fit, double `page_capacity` and `set_len` the file. Doubling makes growth amortised O(1) instead of one syscall per page, and an explicit `set_len` keeps `get_db_file_size` predictable instead of letting a write past the end extend the file as a side effect. The subtle part is the order of the two updates: if `set_len` fails after you have bumped the counters, the structure claims room the file does not have. Pick an order, and make sure an I/O error leaves a state you can describe.
