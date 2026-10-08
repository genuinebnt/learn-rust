**Where this fits.** Sorted pages insert in the middle. That means moving the entries after the insertion point one slot to the right.

## The task

Implement `insert_at(index, len, &value)` in `src/storage/page/page_array.rs`: the array currently holds `len` entries; shift entries `index..len` **one entry to the right** and store `value` at `index`. Panic with a message containing "no room" if `index > len` or if the array has no room for `len + 1` entries.

## Tests

- Insert in the middle, at the front, at the end, into an empty array; filling the array exactly.
- Overlapping moves don't smear (`[10,20,30,40,50,60]` + front insert: every entry shifts correctly).
- Full array or index past `len`: panic. A model test: 64 random inserts agree with `Vec::insert`.

## Syntax and methods

```rust
self.bytes.as_mut().copy_within(index * size..len * size, (index + 1) * size);   // memmove: the source and destination overlap
self.set(index, value);
```

## Notes

**`copy_within` is `memmove`, not `memcpy`.** When the source and destination ranges overlap, copying front to back overwrites entries before they are read (every entry becomes a copy of the first). `memmove`, and `copy_within`, copy as if through a temporary buffer. `copy_from_slice` can't overlap at all: the borrow checker won't let you have `&mut` and `&` into the same slice.

## In BusTub

```cpp
// B+ tree leaf insert (what students write): shift [index, size) right by one
for (int i = GetSize(); i > index; i--) { array_[i] = array_[i - 1]; }      // a backward loop: correct
std::memmove(array_ + index + 1, array_ + index, (GetSize() - index) * sizeof(MappingType));   // the one-liner
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `memmove(dst, src, n)` (overlap OK) vs `memcpy(dst, src, n)` (overlap is **undefined behaviour**) | `copy_within(range, dest)` vs `copy_from_slice` |
| `std::copy_backward(first, last, d_last)` / `std::move_backward` for right shifts | `copy_within` handles direction itself |
| `std::vector::insert(it, value)` O(n) shift, invalidating iterators | `Vec::insert(index, value)`; here the "vector" is page bytes |
| `memmove` with a byte count: easy to forget `* sizeof(T)` | `index * size` explicit in the code and in the tests |

**Port rule:** `memcpy` between ranges that might overlap is a latent bug in C/C++; port it as `copy_within`.

## Learn more
- [`copy_within`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within) · C++ [`memmove`](https://en.cppreference.com/w/cpp/string/byte/memmove) vs [`memcpy`](https://en.cppreference.com/w/cpp/string/byte/memcpy) · [`Vec::insert`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.insert)
