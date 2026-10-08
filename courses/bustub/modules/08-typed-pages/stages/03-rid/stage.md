**Where this fits.** An index maps keys to **record ids**: (the page a tuple is on, its slot on that page). Hash table and B+ tree leaves store them.

## The task

`Rid` (`src/storage/page/page_bytes.rs`) has its fields, `new`, accessors and `Default` (the invalid rid) given. Implement:
- `get() -> i64`: the whole rid as one integer, the page id in the **high 32 bits** and the slot in the **low 32**;
- `from_i64(i64) -> Rid`: the inverse.

## Tests

- `Rid::new(PageId(1), 2).get()` is `(1 << 32) | 2`; page 0 slot 5 is 5; page 3 slot 0 is `3 << 32`.
- A **negative** page id keeps its sign (`-1` page, slot 0 is `-(1 << 32)`), and round trips.
- The slot never leaks into the page: slot `u32::MAX` round trips and the high half is untouched. 100 random round trips. The default rid is invalid.

## Syntax and methods

```rust
((self.page_id.0 as i64) << 32) | self.slot_num as i64     // i32 -> i64 sign-extends; u32 -> i64 zero-extends
PageId((rid >> 32) as i32)     // >> on a signed integer is arithmetic (keeps the sign); `as i32` keeps the low 32 bits
rid as u32                     // truncating cast: the low 32 bits
```

## Notes

**Casts do the packing.** Rust's `as` between integer types is defined: widening a signed value sign-extends, widening an unsigned one zero-extends, narrowing keeps the low bits. That is exactly the behaviour the packing needs, but it makes the *order* of casts matter: `(slot as i64)` after `slot: u32` is fine; `(slot as i32) as i64` would sign-extend a slot with the top bit set and corrupt the page id. The test with slot `u32::MAX` is there for that.

## In BusTub

```cpp
inline auto Get() const -> int64_t { return (static_cast<int64_t>(page_id_)) << 32 | slot_num_; }
explicit RID(int64_t rid) : page_id_(static_cast<page_id_t>(rid >> 32)), slot_num_(static_cast<uint32_t>(rid)) {}
```

(Left-shifting a *negative* signed value is undefined behaviour before C++20; Rust defines it.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `static_cast<int64_t>(page_id_) << 32 \| slot_num_`: precedence and promotion rules decide the result | `((page_id as i64) << 32) \| slot as i64`: casts are explicit |
| `class RID` with private fields and a `Get()` | `struct Rid` with private fields; `#[derive(PartialEq, Eq, Hash, Ord)]` replaces `operator==` and `std::hash<RID>` |
| `std::hash<RID>` specialisation in `namespace std` | `#[derive(Hash)]` |
| `RID() = default` giving an invalid rid via in-class initialisers | `impl Default for Rid` |

**Port rule:** `operator==`, `operator<`, `std::hash` specialisations on a plain data class become `#[derive(PartialEq, Eq, PartialOrd, Ord, Hash)]`.

## Learn more
- The Rust Reference: [numeric cast semantics](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast) · [`#[derive]`](https://doc.rust-lang.org/book/appendix-03-derivable-traits.html)
- BusTub [rid.h](https://github.com/cmu-db/bustub/blob/master/src/include/common/rid.h)
