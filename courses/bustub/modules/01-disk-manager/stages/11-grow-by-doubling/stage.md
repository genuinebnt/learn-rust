**Where this fits.** The file started with room for 16 pages. What happens at the 17th?

## The task

`page_capacity` is how many pages the file has room for; the file's length is always `file_size_for(page_capacity)`. In `DbIo::allocate_slot` (`src/storage/disk/disk_manager.rs`), after the fresh slot is chosen: if the slot **doesn't fit** (`slot >= page_capacity`), **double** `page_capacity` and `set_len` the file to the new size.

## Tests

- 16 allocations leave the file at 17 pages; the 17th (slot 16) makes it 33; then 65, then 129.
- 100 pages written leave a file of exactly 129 pages.
- After every allocation from 1 to 200, the size is `(next_power_of_two(max(n, 16)) + 1)` pages. Pages written before a growth still read back after it.

## Syntax and methods

```rust
self.page_capacity *= 2;
self.file.set_len(file_size_for(self.page_capacity))?;
```

## Notes

Why double instead of adding a page each time? Resizing is a system call that may have to move or reserve file blocks. Doubling makes a file of `n` pages resize only `O(log n)` times, so growth is cheap **on average**: the same amortised argument as `Vec::push`.

## In BusTub

```cpp
if (pages_.size() + 1 >= page_capacity_) {
    page_capacity_ *= 2;
    std::filesystem::resize_file(db_file_name_, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
}
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| C: `buf = realloc(buf, new_cap)` (may move; old pointers dangle) | `Vec` grows itself; indexes survive, references don't (the borrow checker enforces it) |
| `std::vector::push_back` grows by 1.5x (MSVC) or 2x (libstdc++, libc++) | `Vec` doubles (amortised O(1)); `Vec::reserve` / `with_capacity` to plan ahead |
| `std::filesystem::resize_file(path, n)`, `ftruncate(fd, n)` | `file.set_len(n)` |
| growth factor 2 wastes up to half the file; 1.5 reuses freed blocks better in allocators | file growth is a design choice either way; BusTub doubles |

**Pitfall in C:** after `realloc`, every pointer into the old block is dangling. The same shape of bug in a buffer pool (a pointer to a frame kept across a resize) is why frames here will be indexed, not pointed to.

## Learn more
- [`Vec` capacity and growth](https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation)
- CMU 15-445 lecture "Database Storage I": how the file is organised into pages
