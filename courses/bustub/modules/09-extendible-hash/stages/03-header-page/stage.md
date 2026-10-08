**Where this fits.** An extendible hash table has **three levels**. The **header** page is the root: it maps the *top* bits of a hash to one of up to 512 **directory** pages (so a table can grow many directories, each independently). A directory maps the *low* bits to a **bucket** page; a bucket holds the pairs.

## The task

`ExtendibleHTableHeaderPage<B>` (`src/storage/page/extendible_htable_header_page.rs`) is a view over page bytes (`B` is `&[u8]` or `&mut [u8]`), laid out as `| directory_page_ids [i32; 512] | max_depth u32 |` (stage 2a-12). Implement:
- `init(max_depth)`: panic with "does not fit" if `max_depth > 9`; store it, and set **every** slot to `PageId::INVALID`;
- `max_depth()`, `max_size()` (`2^max_depth`);
- `get_directory_page_id(idx)` / `set_directory_page_id(idx, id)`: panic with "out of range" for a slot at or past `max_size`.

## Tests

- After `init(2)`: depth 2, size 4, all slots `INVALID`. Ids round trip; the bytes land where BusTub's layout says (slot 1 at byte 4, max depth at byte 2048). A read-only view works. Slot 4 of a 4-slot header, and depth 10, panic.

## Syntax and methods

```rust
impl<B: AsRef<[u8]>> ExtendibleHTableHeaderPage<B> { fn max_depth(&self) -> u32 { read_u32(self.page.as_ref(), HEADER_MAX_DEPTH_OFFSET) } }
impl<B: AsRef<[u8]> + AsMut<[u8]>> ExtendibleHTableHeaderPage<B> { fn init(&mut self, max_depth: u32) { write_u32(self.page.as_mut(), ..) } }
```

## Notes

**Fresh pages are zeros, and 0 is a real page id.** `init` must write `INVALID` explicitly into every slot, or the table would believe "directory 0 is page 0". (`new_page` hands out zero-filled memory.) The same is true of every on-disk "pointer" field.

**A view is not an object.** C++ casts the page to `ExtendibleHTableHeaderPage *` and calls methods on that pointer. Here the view is a small struct holding the page's bytes (by reference or by value) and reading fields on demand. Two flavours from one struct: `&[u8]` gives the read-only methods, `&mut [u8]` also the writers, so a `ReadPageGuard` can't call `init`.

## In BusTub

```cpp
void ExtendibleHTableHeaderPage::Init(uint32_t max_depth) { /* TODO(P2): set max_depth_ and fill directory_page_ids_ with INVALID_PAGE_ID */ }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ExtendibleHTableHeaderPage() = delete; DISALLOW_COPY_AND_MOVE(...)`: the class can't be constructed, only viewed through a cast pointer | a view struct that holds the bytes; nothing to forbid |
| `page_id_t directory_page_ids_[HTABLE_HEADER_ARRAY_SIZE]; uint32_t max_depth_;` | offsets in `layout.rs` + `read_page_id` / `read_u32` |
| `BUSTUB_ASSERT(directory_idx < MaxSize(), ...)` | `assert!(directory_idx < self.max_size(), "...")` |
| `std::fill(std::begin(a), std::end(a), INVALID_PAGE_ID)` | a loop writing `PageId::INVALID` (or `chunks_exact_mut`) |

**Port rule:** the page *classes* of BusTub become views; their data members become offset constants; `Init()` is the only place a page's bytes are formatted.

## Learn more
- [`AsRef`/`AsMut`](https://doc.rust-lang.org/std/convert/trait.AsRef.html) · BusTub [extendible_htable_header_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_header_page.h) · CMU 15-445 "Hash Tables" (extendible hashing, from slide ~40)
- [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing) (Fagin, Nievergelt, Pippenger, Strong, 1979)
