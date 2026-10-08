**Where this fits.** A page that was never written, or only partly written, must read as zeros.

## The task

Implement `read_slot(file, slot, buf)` in `src/storage/disk/disk_manager.rs`: read the slot into `buf` with `read_full_at`, then set **every byte it didn't fill** to `0`. The buffer may hold anything on the way in.

## Tests

- A slot written with `write_slot` reads back identical.
- A 100-byte file read as slot 0: the first 100 bytes come back, the other 8092 are zero (even if the buffer was full of `0xFF`).
- A slot far past the end is all zeros. A slot that ends exactly at the end of the file needs no filling.

## Syntax and methods

```rust
buf[n..].fill(0);        // set every element of a slice to a value; n == buf.len() is fine (empty slice)
```

## In BusTub

```cpp
if (read_count < BUSTUB_PAGE_SIZE) {
    db_io_.clear();                                              // un-fail the stream after hitting EOF
    memset(page_data + read_count, 0, BUSTUB_PAGE_SIZE - read_count);
}
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `memset(buf + n, 0, size - n);` | `buf[n..].fill(0);` |
| if `n > size`, `size - n` wraps (it's unsigned) and `memset` writes gigabytes: **a buffer overflow** | `buf[n..]` panics on `n > len` (a bounds check); never memory corruption |
| `char buf[PAGE_SIZE]` decays to `char *` and forgets its length when passed to a function | `&mut PageData` is `&mut [u8; 8192]`: the length is part of the type |
| `std::array<char, N>`, `std::span<char>` (C++20) | `[u8; N]`, `&mut [u8]` |

**Port rule:** `(char *p, size_t n)` pairs become one slice `&[u8]` / `&mut [u8]`; a pointer to a fixed-size buffer becomes `&[u8; N]`.

## Learn more
- [`<[T]>::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill)
