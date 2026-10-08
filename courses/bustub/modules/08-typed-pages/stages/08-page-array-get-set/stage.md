**Where this fits.** The last member of BusTub's bucket page is `MappingType array_[N]`: an array that continues to the end of the page. Rust has no flexible array member, so this stage builds one: a view over a byte range that reads and writes entries by index.

## The task

`PageArray<B, T>` (`src/storage/page/page_array.rs`) wraps any byte container `B` (a `&[u8]` to read, a `&mut [u8]` or `Vec<u8>` to write) and views it as entries of `T: FixedSize`. `new` and `capacity` are given. Implement `get(index) -> T` and `set(index, &T)`. Both **panic**, with a message containing "past the capacity", for an index the bytes can't hold.

## Tests

- `set` then `get`; entries don't overlap; the capacity counts whole entries only (35 bytes of `(i32, i32)` is 4 entries).
- A read-only view over `&[u8]`, a writable one over `&mut [u8]`, and one over an owned `Vec<u8>` all work; out-of-range `get`/`set` panic.

## Syntax and methods

```rust
pub struct PageArray<B, T> { bytes: B, _entry: PhantomData<T> }                 // PhantomData<T>: "this type uses T" without storing one
impl<B: AsRef<[u8]>, T: FixedSize> PageArray<B, T> { ... self.bytes.as_ref() ... }     // reading needs AsRef<[u8]>
impl<B: AsRef<[u8]> + AsMut<[u8]>, T: FixedSize> PageArray<B, T> { ... self.bytes.as_mut() ... }   // writing needs AsMut too
T::decode(&self.bytes.as_ref()[at..at + T::SIZE])
```

## Notes

**One type, read-only or writable, depending on what you give it.** `AsRef<[u8]>` is implemented by `&[u8]`, `&mut [u8]`, `Vec<u8>`, `[u8; N]`...; `AsMut<[u8]>` only by the mutable ones. So `get` exists for every `PageArray`, `set` only for writable ones: a `ReadPageGuard`'s page can't be modified through a `PageArray` because the types won't allow it. In C++ this needs a `const` and a non-`const` class or a `const_cast`.

**`PhantomData`.** The struct needs a `T` in its signature (so the compiler knows which entry type this array holds) but stores no `T`; `PhantomData<T>` is a zero-sized marker that says so.

## In BusTub

```cpp
MappingType array_[HTableBucketArraySize(sizeof(MappingType))];   // a flexible tail: "array_[0]" in B+ tree pages
auto KeyAt(uint32_t bucket_idx) const -> KeyType { return array_[bucket_idx].first; }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a flexible array member `T array_[0];` or `T array_[]`: its length is unknown to the type system, access is unchecked | `PageArray` over a slice: the length is the slice's, access is checked |
| `reinterpret_cast<MappingType *>(page_data + 8)` then `array_[i]` | `T::decode(&bytes[i * SIZE..(i + 1) * SIZE])` |
| `const T &operator[](i) const` and `T &operator[](i)` | `get(i) -> T` (a copy: entries are small `FixedSize` values) and `set(i, &T)` |
| `array_[i]` with `i` past the end: out-of-bounds read or write | panic with a clear message |

**Port rule:** a flexible array member becomes a view over the trailing bytes; if C++ hands out references into it (`T &operator[]`), decide whether callers need a copy (`get`) or an in-place edit (`set`, or `with_mut(i, |t| ..)`).

## Learn more
- [`PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) · [`AsRef`](https://doc.rust-lang.org/std/convert/trait.AsRef.html) / [`AsMut`](https://doc.rust-lang.org/std/convert/trait.AsMut.html)
- Postgres' [`bufpage.h`](https://github.com/postgres/postgres/blob/master/src/include/storage/bufpage.h) (the page layout it reads by offset) · SQLite [`btreeInt.h`](https://github.com/sqlite/sqlite/blob/master/src/btreeInt.h)
