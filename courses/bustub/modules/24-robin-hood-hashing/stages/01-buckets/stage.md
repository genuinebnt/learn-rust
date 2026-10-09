Before any key is stored, the table needs its vocabulary: how many buckets, which bucket a key *wants* (its **home**), and how far from home a bucket is (the **probe distance**, counted forward and wrapping around the end of the table). Everything in the next stages is built from these.

## The task

In `src/primer/robin_hood_hash_set.rs`:

- `RobinHoodHashSet::new(capacity)`: `Err(Invalid)` for capacity 0; otherwise a table of `capacity` empty slots and size 0.
- `home_bucket(key)`: `key.robin_hood_hash() % capacity` (the hash trait is given: for integers it is `key × 0x9e3779b97f4a7c15` with wrapping arithmetic, BusTub's constant).
- `probe_distance(home, bucket)`: the number of steps forward from `home` to `bucket`, wrapping.
- `size()` (live keys, under the read lock) and `load_factor()` (`size / capacity`).

## Tests

- A new set has its capacity, bucket count, size 0 and load factor 0.
- Capacity 0 is an error.
- The home bucket is the hash modulo the capacity.
- Probe distance counts forward and wraps.
- The integer hash is the multiplicative one; strings hash deterministically.

## Syntax and methods

```rust
(bucket + self.capacity - home) % self.capacity      // no negative numbers with unsigned types
key.robin_hood_hash() % self.capacity
vec![Slot::Empty; capacity]                          // needs Slot: Clone
```

## Notes

**Wraparound without subtraction underflow.** `bucket - home` fails when `bucket < home`. Adding `capacity` first keeps the arithmetic non-negative; the final `% capacity` handles the case where no wrap happened.

**Why a multiplicative hash.** Sequential integer keys would otherwise land in sequential buckets and look perfectly distributed; multiplying by a large odd constant scatters them. Tests pick keys *by home bucket* using exactly this hash, which is why it is pinned.

**Slots.** `Empty`, `Tombstone` and `Live(key)`: a three-state enum instead of a flag next to a possibly uninitialised key.

## In BusTub

`robin_hood_hash_set.h`: "`/** A fixed-capacity, concurrent hash set using Robin Hood open addressing. */`" and `RobinHoodHash<int>`: "`return static_cast<size_t>(static_cast<uint64_t>(static_cast<int64_t>(key)) * 0x9e3779b97f4a7c15ULL);`". The test helper `FindKeysWithHomeBucket` selects colliding keys with it.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw std::invalid_argument` in the constructor | `new(...) -> Result<Self, Exception>` |
| `std::vector<Bucket>` with a `state_` byte | `Vec<Slot<K>>` with an enum |

**Port rule:** a constructor that can reject its arguments returns `Result`.

## Learn more
- [Fibonacci hashing](https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/) · [`u64::wrapping_mul`](https://doc.rust-lang.org/std/primitive.u64.html#method.wrapping_mul)

## Performance

All four functions are constant time. `% capacity` is a division; real tables use a power-of-two capacity and a mask, which BusTub's header mentions with its mixing function for strings.

**Measure it.** Compare `% capacity` with `& (capacity - 1)` over 100 million keys; the mask is several times faster.

## Hints

### Cast carefully

The hash is a `usize`; keep the arithmetic in `usize` throughout.

### Test the wrap by hand

`probe_distance(6, 0)` in a table of 8 is 2 (buckets 7 and 0).
