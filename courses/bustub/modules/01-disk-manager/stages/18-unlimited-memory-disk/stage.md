**Where this fits.** Most of BusTub's tests use this disk: no capacity to choose, pages appear when first written.

## The task

Pages live in a `Vec<Option<Box<PageData>>>` indexed by page id; `None` means "never written". In `disk_manager_memory.rs`, `DiskManagerUnlimitedMemory`:
- `write_page`: grow the `Vec` to length `id + 1` (filled with `None`), create the page if it is `None`, copy the data in, count the write;
- `read_page`: copy the page out if it exists, otherwise zero the buffer. Reading never creates a page;
- `get_memory_usage`: the number of existing pages times `BUSTUB_PAGE_SIZE`.

## Tests

- Pages 0, 1, 500 and 5000 read back; a page never written, or in a gap below a written page, reads as zeros.
- Rewriting replaces the page. Memory usage counts only pages that exist: two pages written is `2 * 8192`, a rewrite or a read of a missing page doesn't change it.
- `copy_page` (stage 16) works on this disk too.
- Eight threads write 25 pages each; all 200 read back and `get_num_writes` is 200. `PageId::INVALID` panics.

## Syntax and methods

```rust
pages.resize_with(at + 1, || None);                  // grow, filling new slots with the closure's result
let page = pages[at].get_or_insert_with(|| Box::new([0u8; BUSTUB_PAGE_SIZE]));   // &mut Box<PageData>
page.copy_from_slice(data);                           // a Box<[u8; N]> derefs to the array
match pages.get(at) { Some(Some(page)) => buf.copy_from_slice(&**page), _ => buf.fill(0) }
pages.iter().filter(|p| p.is_some()).count()
```

## Notes

Why `Option<Box<..>>` and not `Option<PageData>`? A `PageData` is 8 KiB, so a `Vec` of them reserves 8 KiB for every id up to the highest written. `Option<Box<T>>` is **one pointer wide** (the null pointer means `None`, a "niche"), so empty ids cost 8 bytes.

## In BusTub

```cpp
if (page_id >= static_cast<int>(data_.size())) { data_.resize(page_id + 1); }
if (data_[page_id] == nullptr) { data_[page_id] = std::make_shared<ProtectedPage>(); }
memcpy(ptr->first.data(), page_data, BUSTUB_PAGE_SIZE);
```

BusTub's version also has a **latency simulator** (sleeping 1 ms per random access, 0.1 ms for nearby pages) so tests can see a buffer pool hide disk latency. It comes in with the buffer pool module.

## The C/C++ way
| C++ | Rust |
|---|---|
| `std::vector<std::shared_ptr<Page>> data_; data_.resize(n);` | `Vec<Option<Box<PageData>>>`; `resize_with(n, \|\| None)` |
| a null pointer means "no page": `if (data_[i] == nullptr)` | `None`; `Option<Box<T>>` is the same size as a pointer, and `None` *is* the null pointer |
| `std::make_shared<T>()` | `Box::new(..)` for sole ownership; `Arc::new(..)` only if it is really shared |
| `std::optional<T>` | `Option<T>` |
| `std::shared_mutex` per page (BusTub's `ProtectedPage`) | `RwLock<..>`: a later stage when pages are shared |
| `std::this_thread::get_id()` | `std::thread::current().id()` |

**Port rule:** `shared_ptr` is the *last* resort in Rust, not the default. Ask "who owns this?": one owner means `Box`, many means `Arc`. BusTub uses `shared_ptr` liberally because C++ has no other cheap way to say "keep this alive".

## Learn more
- [`Option::get_or_insert_with`](https://doc.rust-lang.org/std/option/enum.Option.html#method.get_or_insert_with) · [`Vec::resize_with`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.resize_with) · [niche optimisation](https://doc.rust-lang.org/std/option/index.html#representation)
