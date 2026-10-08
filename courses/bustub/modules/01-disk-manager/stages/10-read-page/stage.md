**Where this fits.** The other half of the page table. Now a page can make the round trip.

## The task

Implement `read_page(page_id, buf)` in `src/storage/disk/disk_manager.rs`: if the page has a slot, `read_slot` it into `buf`; if it has never been written, fill `buf` with zeros. Reading must **not** change anything (no slot is allocated).

## Tests

- A page reads back what was written; ten pages don't interfere with each other.
- A page never written reads as zeros, even into a buffer full of `0xFF`.
- Reading five unknown pages allocates nothing: the next fresh slot is still `0`.

## Syntax and methods

```rust
match io.pages.get(&page_id) {
    Some(&slot) => read_slot(&io.file, slot, buf),   // returns io::Result<()>
    None => { buf.fill(0); Ok(()) }
}
```

## In BusTub

```cpp
if (pages_.find(page_id) != pages_.end()) { offset = pages_[page_id]; }
else { offset = AllocatePage(); }       // BusTub allocates a slot even for a read of an unknown page!
```

One difference on purpose: this port's reads never allocate.

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `void ReadPage(page_id_t id, char *page_data)`: an out-parameter, size known only by convention | `read_page(&self, id: PageId, buf: &mut PageData)`: the type is `&mut [u8; 8192]` |
| `page_id_t` is `int32_t`; `INVALID_PAGE_ID = -1` is a magic value anyone can pass | `PageId(i32)` newtype; `PageId::INVALID` only for on-disk formats; `Option<PageId>` in memory |
| errors: ignored return codes, or logged and returned (`LOG_DEBUG("I/O error"); return;`) | `io::Result<()>`: the caller must handle or `?` it |
| `memset(page, 0, size)` | `buf.fill(0)` |

**Port rule:** an out-parameter pointer (`T *out`) becomes `&mut T` or, better, a return value (`-> T`); here the page buffer stays an out-parameter because the caller owns the 8 KiB.

## Learn more
- [`match`](https://doc.rust-lang.org/book/ch06-02-match.html) on `Option` · BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp) `ReadPage`
