**Where this fits.** The table hashes keys of any `FixedSize` type: ints, `GenericKey<8>`, ...

## The task

In `src/container/hash/hash_function.rs`, implement `HashFunction::get_hash(&self, key: &K) -> u64`: encode the key into its bytes (`K::SIZE` of them, via `FixedSize::encode`), hash them with `murmur_hash3_x64_128` (seed 0), and return the **first** 64-bit half. The table's private `hash` method (in `src/container/disk/hash/disk_extendible_hash_table.rs`, also part of this stage) then truncates it to 32 bits: `as u32`, the low half.

## Tests

- Ints 0, 1, 2, 3, 7, 8, 100, -1, 123456789 hash to the values BusTub's C++ produces (4 bytes of the int, little-endian). `GenericKey<8>` keys hash by their 8 bytes. Only the first half of the 128 bits is kept.
- The low two bits of the hashes of 0..16 spread over all four values (the table uses low bits for buckets).

## Syntax and methods

```rust
let mut bytes = vec![0u8; K::SIZE];
key.encode(&mut bytes);
murmur_hash3_x64_128(&bytes, 0)[0]
self.hash_fn.get_hash(key) as u32       // `as u32` on a u64 keeps the low 32 bits
```

## Notes

**What gets hashed.** BusTub hashes `sizeof(KeyType)` raw bytes of the key object: for an `int`, its 4 bytes in host order. The port hashes the key's *page encoding* (little-endian), which is the same bytes on the x86/ARM machines BusTub runs on. Rust's own `std::hash::Hash`/`Hasher` is a different design: it feeds a key's *fields* into a hasher and is allowed to change between releases; it is not stable enough to base a persistent structure on. A database needs a hash whose output never changes (it decides where data lives on disk).

## In BusTub

```cpp
virtual auto GetHash(KeyType key) const -> uint64_t {
  uint64_t hash[2];
  murmur3::MurmurHash3_x64_128(reinterpret_cast<const void *>(&key), static_cast<int>(sizeof(KeyType)), 0, reinterpret_cast<void *>(&hash));
  return hash[0];
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <typename KeyType> class HashFunction` with a `virtual GetHash` | `struct HashFunction<K>` + a method; override by writing another type with the same method and making the table generic over it |
| `std::hash<T>` (implementation-defined, can vary between runs and compilers) | `std::hash::Hash` + `Hasher` (also unstable across releases; `RandomState` is seeded per process) |
| `reinterpret_cast<const void *>(&key)`: hashes padding bytes and host byte order | `key.encode(&mut bytes)`: explicit bytes |
| `uint64_t hash[2]; ...; return hash[0];` | `murmur_hash3_x64_128(..)[0]` |

**Port rule:** a hash used only in memory can be `std::hash`/`ahash`/`FxHash`; a hash whose value is persisted or must match another system needs a fixed, specified algorithm (Murmur3, xxHash, CityHash, SipHash with a fixed key).

## Learn more
- [`std::hash::Hash`](https://doc.rust-lang.org/std/hash/trait.Hash.html) and [`Hasher`](https://doc.rust-lang.org/std/hash/trait.Hasher.html) · [`RandomState`](https://doc.rust-lang.org/std/collections/hash_map/struct.RandomState.html) · [`ahash`](https://docs.rs/ahash), [`rustc-hash`](https://docs.rs/rustc-hash) (fast in-memory hashers)
- BusTub [hash_function.h](https://github.com/cmu-db/bustub/blob/master/src/include/container/hash/hash_function.h) · C++ [`std::hash`](https://en.cppreference.com/w/cpp/utility/hash)
