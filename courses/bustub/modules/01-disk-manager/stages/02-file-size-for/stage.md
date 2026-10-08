**Where this fits.** The db file is created with room for a number of pages. How many bytes is that?

## The task

Implement `file_size_for(capacity)` in `src/storage/disk/disk_manager.rs`: the byte length of a db file with room for `capacity` pages. BusTub keeps **one spare page** at the end, so the length is `capacity + 1` pages. Reuse `slot_offset`.

## Tests

- `file_size_for(0)` is one page, `8192`.
- `file_size_for(16)` is `17 * 8192` = `139264`.
- `file_size_for(32) - file_size_for(16)` is 16 pages.

## Syntax and methods

Nothing new: a function call. `slot_offset(n)` is "the offset where slot `n` starts", which is also "the length of a file that holds `n` slots".

## In BusTub

```cpp
std::filesystem::resize_file(db_file_name_, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `#define BUSTUB_PAGE_SIZE 8192` (macro, untyped, no scope) | `pub const BUSTUB_PAGE_SIZE: usize = 8192;` (typed, scoped, in `config.rs`) |
| `static constexpr int BUSTUB_PAGE_SIZE = 8192;` (BusTub's `config.h`) | same; and a `const fn` can use it at compile time |
| `(capacity + 1) * kPageSize` in `int` arithmetic | `slot_offset(capacity + 1)`: reuse the function that already does the widening |

**Port rule:** C/C++ constants that size buffers become `const`s of type `usize`; sizes that are file offsets become `u64`.

## Learn more
- BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp), constructor and `AllocatePage`
