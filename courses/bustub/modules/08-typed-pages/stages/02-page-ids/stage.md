**Where this fits.** Pages point at other pages (a directory at its buckets, a B+ tree node at its child). On disk there is no `Option`; "no page" is a special value.

## The task

In `src/storage/page/page_bytes.rs`:
- `read_page_id(page, offset)` / `write_page_id(page, offset, id)`: a `PageId` is an `i32` stored in 4 little-endian bytes. **Signed**: `-1` must survive.
- `read_optional_page_id` / `write_optional_page_id`: the same, but `PageId::INVALID` (`-1`) is `None` in memory.

## Tests

- Ids round trip; `INVALID` is stored as `FF FF FF FF`.
- `None` is stored as `INVALID` and read back as `None`; `Some(PageId(0))` stays `Some`: **0 is a real page**, only -1 means none.
- A zero-filled page reads as page 0 (a lesson in why new pages must write `INVALID` explicitly).

## Syntax and methods

```rust
PageId(i32::from_le_bytes(page[offset..offset + 4].try_into().unwrap()))
Some(read_page_id(page, offset)).filter(|id| id.is_valid())     // Option::filter: keep the Some only if the predicate holds
id.unwrap_or(PageId::INVALID)
```

## Notes

**In memory use `Option`, on disk use a sentinel.** The sentinel is a *storage format* decision (BusTub's `INVALID_PAGE_ID = -1`); `Option<PageId>` is what your code should pass around. Convert at the boundary, exactly once, in these two functions. The bug to avoid is a zero-filled fresh page whose "next page" field reads as page 0 instead of "none": code that walks a page chain then loops into page 0.

## In BusTub

```cpp
static constexpr int INVALID_PAGE_ID = -1;   // size of the fields: static_assert(sizeof(page_id_t) == 4)
page_id_t next_page_id_ = INVALID_PAGE_ID;   // in B+ tree leaves: the sibling pointer
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `int32_t` page ids, `-1` as "none", compared by hand everywhere (`if (id == INVALID_PAGE_ID)`) | `PageId(i32)` with `is_valid()`; `Option<PageId>` in code |
| `static_assert(sizeof(page_id_t) == 4)` | `const _: () = assert!(size_of::<PageId>() == 4);` |
| signed vs unsigned mismatch: `uint32_t` read of a `-1` field gives 4294967295 | read as `i32` explicitly |
| `std::optional<page_id_t>` (not storable in a page: it has a hidden bool) | the same: never put an `Option` in an on-disk struct |

## Learn more
- [`Option::filter`](https://doc.rust-lang.org/std/option/enum.Option.html#method.filter) · [`Option::unwrap_or`](https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or) · Tony Hoare's ["billion dollar mistake"](https://en.wikipedia.org/wiki/Null_pointer#History) (why `Option` exists)
