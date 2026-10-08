This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · PageArray: an array of entries inside a page

**Where this fits.** The last member of BusTub's bucket page is `MappingType array_[N]`: an array that continues to the end of the page. Rust has no flexible array member, so this stage builds one: a view over a byte range that reads and writes entries by index.

### The task

`PageArray<B, T>` (`src/storage/page/page_array.rs`) wraps any byte container `B` (a `&[u8]` to read, a `&mut [u8]` or `Vec<u8>` to write) and views it as entries of `T: FixedSize`. `new` and `capacity` are given. Implement `get(index) -> T` and `set(index, &T)`. Both **panic**, with a message containing "past the capacity", for an index the bytes can't hold.

### Tests

- `set` then `get`; entries don't overlap; the capacity counts whole entries only (35 bytes of `(i32, i32)` is 4 entries).
- A read-only view over `&[u8]`, a writable one over `&mut [u8]`, and one over an owned `Vec<u8>` all work; out-of-range `get`/`set` panic.

### Syntax and methods

```rust
pub struct PageArray<B, T> { bytes: B, _entry: PhantomData<T> }                 // PhantomData<T>: "this type uses T" without storing one
impl<B: AsRef<[u8]>, T: FixedSize> PageArray<B, T> { ... self.bytes.as_ref() ... }     // reading needs AsRef<[u8]>
impl<B: AsRef<[u8]> + AsMut<[u8]>, T: FixedSize> PageArray<B, T> { ... self.bytes.as_mut() ... }   // writing needs AsMut too
T::decode(&self.bytes.as_ref()[at..at + T::SIZE])
```

### Notes

**One type, read-only or writable, depending on what you give it.** `AsRef<[u8]>` is implemented by `&[u8]`, `&mut [u8]`, `Vec<u8>`, `[u8; N]`...; `AsMut<[u8]>` only by the mutable ones. So `get` exists for every `PageArray`, `set` only for writable ones: a `ReadPageGuard`'s page can't be modified through a `PageArray` because the types won't allow it. In C++ this needs a `const` and a non-`const` class or a `const_cast`.

**`PhantomData`.** The struct needs a `T` in its signature (so the compiler knows which entry type this array holds) but stores no `T`; `PhantomData<T>` is a zero-sized marker that says so.

### In BusTub

```cpp
MappingType array_[HTableBucketArraySize(sizeof(MappingType))];   // a flexible tail: "array_[0]" in B+ tree pages
auto KeyAt(uint32_t bucket_idx) const -> KeyType { return array_[bucket_idx].first; }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a flexible array member `T array_[0];` or `T array_[]`: its length is unknown to the type system, access is unchecked | `PageArray` over a slice: the length is the slice's, access is checked |
| `reinterpret_cast<MappingType *>(page_data + 8)` then `array_[i]` | `T::decode(&bytes[i * SIZE..(i + 1) * SIZE])` |
| `const T &operator[](i) const` and `T &operator[](i)` | `get(i) -> T` (a copy: entries are small `FixedSize` values) and `set(i, &T)` |
| `array_[i]` with `i` past the end: out-of-bounds read or write | panic with a clear message |

**Port rule:** a flexible array member becomes a view over the trailing bytes; if C++ hands out references into it (`T &operator[]`), decide whether callers need a copy (`get`) or an in-place edit (`set`, or `with_mut(i, |t| ..)`).

### Learn more
- [`PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) · [`AsRef`](https://doc.rust-lang.org/std/convert/trait.AsRef.html) / [`AsMut`](https://doc.rust-lang.org/std/convert/trait.AsMut.html)
- Postgres' [`bufpage.h`](https://github.com/postgres/postgres/blob/master/src/include/storage/bufpage.h) (the page layout it reads by offset) · SQLite [`btreeInt.h`](https://github.com/sqlite/sqlite/blob/master/src/btreeInt.h)

## Part 2 · insert_at: open a gap with copy_within

**Where this fits.** Sorted pages insert in the middle. That means moving the entries after the insertion point one slot to the right.

### The task

Implement `insert_at(index, len, &value)` in `src/storage/page/page_array.rs`: the array currently holds `len` entries; shift entries `index..len` **one entry to the right** and store `value` at `index`. Panic with a message containing "no room" if `index > len` or if the array has no room for `len + 1` entries.

### Tests

- Insert in the middle, at the front, at the end, into an empty array; filling the array exactly.
- Overlapping moves don't smear (`[10,20,30,40,50,60]` + front insert: every entry shifts correctly).
- Full array or index past `len`: panic. A model test: 64 random inserts agree with `Vec::insert`.

### Syntax and methods

```rust
self.bytes.as_mut().copy_within(index * size..len * size, (index + 1) * size);   // memmove: the source and destination overlap
self.set(index, value);
```

### Notes

**`copy_within` is `memmove`, not `memcpy`.** When the source and destination ranges overlap, copying front to back overwrites entries before they are read (every entry becomes a copy of the first). `memmove`, and `copy_within`, copy as if through a temporary buffer. `copy_from_slice` can't overlap at all: the borrow checker won't let you have `&mut` and `&` into the same slice.

### In BusTub

```cpp
// B+ tree leaf insert (what students write): shift [index, size) right by one
for (int i = GetSize(); i > index; i--) { array_[i] = array_[i - 1]; }      // a backward loop: correct
std::memmove(array_ + index + 1, array_ + index, (GetSize() - index) * sizeof(MappingType));   // the one-liner
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `memmove(dst, src, n)` (overlap OK) vs `memcpy(dst, src, n)` (overlap is **undefined behaviour**) | `copy_within(range, dest)` vs `copy_from_slice` |
| `std::copy_backward(first, last, d_last)` / `std::move_backward` for right shifts | `copy_within` handles direction itself |
| `std::vector::insert(it, value)` O(n) shift, invalidating iterators | `Vec::insert(index, value)`; here the "vector" is page bytes |
| `memmove` with a byte count: easy to forget `* sizeof(T)` | `index * size` explicit in the code and in the tests |

**Port rule:** `memcpy` between ranges that might overlap is a latent bug in C/C++; port it as `copy_within`.

### Learn more
- [`copy_within`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within) · C++ [`memmove`](https://en.cppreference.com/w/cpp/string/byte/memmove) vs [`memcpy`](https://en.cppreference.com/w/cpp/string/byte/memcpy) · [`Vec::insert`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.insert)

## Part 3 · remove_at: close the gap

**Where this fits.** The inverse of the last stage.

### The task

Implement `remove_at(index, len)` in `src/storage/page/page_array.rs`: the array holds `len` entries; shift entries `index + 1..len` **one entry to the left** over entry `index`. Panic with a message containing "no entry" if `index >= len`.

### Tests

- Remove the middle, the first, the last (index `len - 1`: nothing to shift), the only entry.
- Past `len` panics; insert-then-remove restores the array; a model test of 500 random inserts and removes agrees with a `Vec`.

### Syntax and methods

```rust
self.bytes.as_mut().copy_within((index + 1) * size..len * size, index * size);
```

### Notes

Removing doesn't clear the freed last slot: the bytes after `len` are stale. **The length lives outside the array** (in the page header), and every operation takes it as an argument: the array never reads entries at or after `len`. This is a recurring design in database pages: the header is the source of truth, the bytes beyond it are garbage (test `lower_bound` next with exactly that).

### In BusTub

```cpp
void ExtendibleHTableBucketPage::RemoveAt(uint32_t bucket_idx) { /* shift left, then --size_ */ }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::copy(first + 1, last, first)` (left shift: the forward direction is safe) | `copy_within(index + 1..len, index)` |
| `std::vector::erase(it)` | `Vec::remove(index)` |
| the size field maintained by hand next to the shifts (`--size_`) | the caller keeps the length (as the page header does) |
| stale bytes after the logical end: harmless in C++ too, until a bug reads them | the model test compares only `0..len` and a stale-bytes test checks nothing reads past it |

### Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · C++ [`std::vector::erase`](https://en.cppreference.com/w/cpp/container/vector/erase)
