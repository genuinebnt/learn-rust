**Where this fits.** Tests want a disk with no files and no waiting. Two in-memory disks live in `src/storage/disk/disk_manager_memory.rs`; this is the first.

## The task

`DiskManagerMemory::new(capacity)` holds `capacity` pages in one byte buffer: page `n` is bytes `n * 8192 .. (n + 1) * 8192`. Implement `new`, `range` (the bounds check and the byte range of a page), `read_page` and `write_page` (which counts the write). Ids outside `0..capacity` **panic** with a message saying the disk ran out of space: that is a bug in the caller, not an I/O error. A fresh disk reads as zeros. `delete_page` is given (it does nothing).

## Tests

- Pages read back and don't overlap; a fresh disk is all zeros; the count of writes is right.
- Page `capacity`, page 100 on a 4-page disk, and `PageId(-1)` all panic with "ran out of disk space" (reads and writes).
- The disk works as `Arc<dyn DiskIo>`.

## Syntax and methods

```rust
vec![0u8; n]                                        // n zero bytes
assert!(cond, "page {} out of range", id);          // panics with the message when cond is false
let at: std::ops::Range<usize> = start..start + BUSTUB_PAGE_SIZE;
buf.copy_from_slice(&memory[at.clone()]);            // both sides must have the same length, or it panics
self.memory.lock().unwrap()[at].copy_from_slice(data);
```

## In BusTub

```cpp
BUSTUB_ASSERT(static_cast<size_t>(page_id) < page_capacity_, "Ran out of disk space for limited memory disk manager implementation");
size_t offset = static_cast<size_t>(page_id) * BUSTUB_PAGE_SIZE;
memcpy(memory_ + offset, page_data, BUSTUB_PAGE_SIZE);
```

BusTub's `ReadPage` doesn't check the bound at all (undefined behaviour). Here both do.

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `new char[n]` ... `delete[] p` (manual; BusTub's destructor does this) | `vec![0u8; n]`: freed by `Drop` |
| `malloc(n)` is uninitialised; `calloc(1, n)` is zeroed | `vec![0; n]` is always initialised: no "uninitialised read" bug class |
| `memcpy(dst + off, src, size)`: no bounds check; overlapping ranges are UB | `dst[a..b].copy_from_slice(src)`: panics on a length mismatch; `copy_within` for overlap (`memmove`) |
| `BUSTUB_ASSERT(cond, "msg")` (aborts in debug builds) | `assert!(cond, "msg {}", x)` (a panic; in every build unless you use `debug_assert!`) |
| `assert(x)` from `<assert.h>` vanishes with `-DNDEBUG` | `assert!` always runs; `debug_assert!` is the vanishing one |

**Pitfall in the C++:** `DiskManagerMemory::ReadPage` has no bounds check at all, so reading past the end is undefined behaviour. Rust slices make that a panic.

## Learn more
- [`copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · [`assert!`](https://doc.rust-lang.org/std/macro.assert.html) · [`Range`](https://doc.rust-lang.org/std/ops/struct.Range.html)
