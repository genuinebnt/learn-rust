**Where this fits.** BusTub's indexes are generic over the key: an `int`, a `GenericKey<8>`, `GenericKey<64>`. A `GenericKey<N>` is `N` bytes; what they mean is the comparator's business.

## The task

`GenericKey<const KEY_SIZE: usize>` in `src/storage/index/generic_key.rs` has a public `data: [u8; KEY_SIZE]` and `Default` (all zeros). Implement:
- `set_from_integer(i64)`: zero the key, then store the integer little-endian in the first 8 bytes (BusTub: "for test purpose only");
- `get_as_integer()`: the first 8 bytes as an `i64`;
- `FixedSize for GenericKey<N>`: `SIZE = N`, `encode`/`decode` copy the bytes.

## Tests

- `set_from_integer(42)` / `-7` read back; setting a key that held `0xFF…` clears the bytes after the integer.
- Encoding gives the little-endian bytes; sizes 8, 32, 64 all work; the default is zero.

## Syntax and methods

```rust
pub struct GenericKey<const KEY_SIZE: usize> { pub data: [u8; KEY_SIZE] }     // a const generic parameter: the size is part of the type
impl<const KEY_SIZE: usize> GenericKey<KEY_SIZE> { ... }
self.data[..8].copy_from_slice(&key.to_le_bytes());
```

## Notes

**Const generics.** `GenericKey<8>` and `GenericKey<64>` are different types, and the array length is checked by the compiler: you can't pass a 64-byte key where an 8-byte one is expected. C++'s `template <size_t KeySize>` is the same idea. `[u8; KEY_SIZE]` lives inline in the struct (no heap), so a page full of keys is one contiguous run of bytes, which is the whole point of a fixed-size key.

## In BusTub

```cpp
template <size_t KeySize> class GenericKey {
  inline void SetFromInteger(int64_t key) { memset(data_, 0, KeySize); memcpy(data_, &key, sizeof(int64_t)); }
  inline auto GetAsInteger() const -> int64_t { int64_t out; memcpy(&out, data_, sizeof(int64_t)); return out; }
  char data_[KeySize];
};
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <size_t KeySize>` | `<const KEY_SIZE: usize>` |
| `char data_[KeySize]` (signedness of `char` is implementation-defined) | `[u8; KEY_SIZE]` (always unsigned) |
| `memset(data_, 0, KeySize); memcpy(data_, &key, 8)` | `self.data = [0; KEY_SIZE]; self.data[..8].copy_from_slice(&key.to_le_bytes())` |
| `memcpy(&out, data_, sizeof(int64_t))` into an uninitialised local | `i64::from_le_bytes(self.data[..8].try_into().unwrap())`: no uninitialised memory exists |
| `reinterpret_cast<int64_t *>(data_)` in `ToString()`: strict-aliasing UB | the safe read above |

## Learn more
- The Rust Reference: [const generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics) · [`[T; N]` arrays](https://doc.rust-lang.org/std/primitive.array.html)
- BusTub [generic_key.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/index/generic_key.h)
