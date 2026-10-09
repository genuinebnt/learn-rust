The heart of the set. **Insert** probes forward from the home bucket carrying a key; at each bucket: if it is free, put the carried key there; if it holds a key *closer to its own home* than the carried key is to its, **swap** (the carried key takes the bucket, the resident becomes the carried key and keeps probing). **Lookup** probes forward from the home until it finds the key or an empty bucket.

## The task

In `src/primer/robin_hood_hash_set.rs`:

- `find(table, key) -> Option<usize>` (private): probe `capacity` steps from the home bucket, wrapping: an `Empty` bucket ends the search; a `Tombstone` is probed past; a `Live` equal key is the answer; any other `Live` key is probed past.
- `insert(&key) -> bool`: write lock; if `find` finds an equal key, replace it and return `true`; if `size == capacity` return `false` **before touching anything**; otherwise probe from the home bucket carrying `(key, home)`: `Empty` or `Tombstone`: store, size + 1, `true`; `Live(resident)` with a smaller probe distance than the carried key's: swap, carry the resident (and its home) on; go to the next bucket.
- `contains` (read lock, `find`) and `get_bucket` (the bucket found, or `bucket_count()`).

## Tests

- Insert, duplicate replacement, lookup, size and load factor; strings.
- A one-bucket table holds one key.
- A key further from home takes the bucket of a closer one (BusTub's displacement scenario: `a, b, c` with home 0 and `d` with home 1 end at buckets 0, 1, 2, 3 in the order the test checks).
- Insert fails only when every bucket is taken, and nothing is lost when it does.
- Probing wraps; absent keys are reported absent in a crowded table; all keys are found after many displacements.

## Syntax and methods

```rust
let Slot::Live(displaced) = std::mem::replace(&mut table.slots[bucket], Slot::Live(carried)) else { unreachable!() };
carried = displaced;
home = resident_home;
bucket = (bucket + 1) % self.capacity;
```

## Notes

**Why `find` does not stop early.** The textbook rule "stop at a resident closer to home than I would be" is only valid if every key stays where Robin Hood insertion put it. Stage 3 adds tombstones, and a tombstone can be reused by a key with a short probe distance, sitting in front of keys that probed further. A lookup that stops there misses them. So lookups go to an empty bucket; displacement during insert still keeps the longest probe short.

**Why the full-table check comes first.** With fewer live keys than buckets, a free bucket exists, and the probe loop finds it. Without the check, a full table makes the loop swap residents around the whole circle and then fail, having moved keys and lost one.

**Replacing an equal key.** For integers it changes nothing visible; for a key type with identity beyond equality it stores the new value. That is what `Insert` returning `true` for an existing key means in BusTub's header ("`true when a key is inserted or an existing equal key is replaced`").

## In BusTub

`robin_hood_hash_set.cpp`: "`@TODO(student) Insert with linear probing, Robin Hood displacement, and safe concurrent access.`" and "`@TODO(student) Probe through tombstones and stop only where correctness permits.`". The tests `CollisionAndRobinHoodDisplacementTest`, `FullTableTest`, `WraparoundTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::swap(carried, bucket.key)` | `std::mem::replace(&mut slots[i], Slot::Live(carried))` |
| `std::unique_lock<std::shared_mutex>` | `self.table.write().unwrap()` |
| `size_t` arithmetic that can underflow silently | `usize` arithmetic that panics in debug builds if you subtract too much |

**Port rule:** swapping two values that sit in different places is `mem::replace` or `mem::swap`, never a copy.

## Learn more
- [`mem::replace`](https://doc.rust-lang.org/std/mem/fn.replace.html) · [Robin Hood hashing](https://codecapsule.com/2013/11/11/robin-hood-hashing/)

## Performance

At load factor 0.75, linear probing alone can leave some keys far from home; Robin Hood keeps the longest probe near `log n` (measured below). The cost is the extra comparison and occasional swap on insert. Lookups of present keys are as fast as ever; lookups of absent keys here run until an empty bucket, which at load 0.75 is a handful of probes.

**Measure it.** Insert 200 000 **random** keys into a table of 262 144 and print `max_probe_distance()` (stage 3): about 18 here, close to `log2(200 000) = 17.6`, in about 5 ms; 200 000 lookups of present or absent keys take about 5 ms each (release mode). Do not measure with the keys `0..200 000`: multiplying consecutive integers by an odd constant and taking a power of two modulo is a permutation, so no two keys collide and the longest probe is 0.

## Hints

### Compute the resident's home from the resident

Its probe distance at this bucket is `probe_distance(home_of(resident), bucket)`; you cannot reuse the carried key's home.

### Swap, then keep going

After a swap the displaced key continues from the **next** bucket with its own home.

### A test to write yourself

Insert keys `0..n` into a table of `n + 1` buckets and check every key is found; any lost key points at the swap logic.
