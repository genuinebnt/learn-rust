**Where this fits.** BusTub's bucket page is a C++ template over the key and value types. It works because C++ can ask `sizeof(T)` and `memcpy` a `T`. Rust needs the type to say how big it is and how to turn it into bytes: a trait.

## The task

In `src/storage/page/page_bytes.rs`, `trait FixedSize { const SIZE: usize; fn encode(&self, out: &mut [u8]); fn decode(bytes: &[u8]) -> Self; }` is given. Implement it for `i32`, `u32`, `i64`, `PageId` (an `i32`) and `Rid` (its `i64`). `out`/`bytes` are exactly `SIZE` bytes.

## Tests

- Sizes 4, 4, 8, 4, 8. Every type round trips (including `i32::MIN`, `u32::MAX`, `PageId::INVALID`, the default rid).
- Little-endian: `0x0A0B0C0D` encodes as `0D 0C 0B 0A`. A `PageId` is laid out like its raw `i32`.

## Syntax and methods

```rust
impl FixedSize for i32 {
    const SIZE: usize = 4;                                  // an associated constant: part of the type, known at compile time
    fn encode(&self, out: &mut [u8]) { out.copy_from_slice(&self.to_le_bytes()); }
    fn decode(bytes: &[u8]) -> i32 { i32::from_le_bytes(bytes.try_into().expect("4 bytes")) }
}
```

## Notes

**An associated const is a compile-time `sizeof`.** `T::SIZE` can size an array (`[u8; T::SIZE]` in a `const fn`, with caveats), compute a capacity (next stages), and be checked by `const _: () = assert!(..)`. It works for generics: `fn capacity<T: FixedSize>() -> usize { PAGE / T::SIZE }`, resolved per type at compile time, with no run-time cost: C++ templates, but with the requirement written down (`T: FixedSize`) rather than discovered from error messages.

## In BusTub

```cpp
template <typename KeyType, typename ValueType, typename KeyComparator>
class ExtendibleHTableBucketPage { ...  MappingType array_[HTableBucketArraySize(sizeof(MappingType))]; };
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `sizeof(T)` | `T::SIZE` (explicit) or `std::mem::size_of::<T>()` (the in-memory size, which includes padding: not the same thing) |
| `memcpy(dst, &value, sizeof(T))` for trivially copyable `T` | `value.encode(dst)` |
| `template <typename T> ... static_assert(std::is_trivially_copyable_v<T>)` | `T: FixedSize` bound |
| copying a struct's raw bytes into a page also copies **padding** and host byte order | explicit encoding: nothing hidden |
| concepts (C++20): `template <FixedSize T>` | trait bounds: `fn f<T: FixedSize>()` |

**Port rule:** a C++ template parameter that is only ever used as `sizeof(T)` + `memcpy` is a trait with `SIZE`, `encode`, `decode`.

## Learn more
- The Rust Book: [traits](https://doc.rust-lang.org/book/ch10-02-traits.html) and [generics](https://doc.rust-lang.org/book/ch10-01-syntax.html) · The Reference: [associated constants](https://doc.rust-lang.org/reference/items/associated-items.html#associated-constants)
- [`mem::size_of`](https://doc.rust-lang.org/std/mem/fn.size_of.html) and why it isn't `SIZE` · C++ [`templates`](https://en.cppreference.com/w/cpp/language/templates)
