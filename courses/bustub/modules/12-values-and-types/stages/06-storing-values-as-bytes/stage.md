A value that lives only in memory is no use to a database: a tuple is bytes in a page. This stage gives every value a **byte encoding**: how many bytes it takes, how to write it into a buffer and how to read it back. It is the contract the next module's tuples are built on (a tuple is "these values, one after another").

The encoding is BusTub's: fixed-width numbers in **little-endian**, a boolean as one byte, and a string as a **4-byte length, the text and a terminating zero byte**. And NULL is *not* a flag: it is the reserved bit pattern from stage 2 (`i32::MIN` for an integer, a length of `u32::MAX` for a string), which is why deserialising a value is also where "the reserved number means NULL" happens.

## The task

In `src/types/value.rs`:
- `storage_size()`: the number of bytes `serialize_to` writes: the type's size for fixed-size types; for a `Varchar`: `4 + text + 1` (the length field counts the zero byte), and **4** for a NULL string;
- `serialize_to(&self, storage: &mut [u8])`: write the value at the start of `storage`, little-endian. A NULL writes its reserved encoding: `i8::MIN`, `i16::MIN`, `i32::MIN`, `i64::MIN`, `f64::MIN`, `u64::MAX`, a boolean's `i8::MIN` byte, and for a string only the length `u32::MAX`;
- `deserialize_from(storage: &[u8], type_id) -> Result<Value>`: the inverse; it reads only as many bytes as the type needs, a reserved encoding is a NULL (the typed constructors already do this for numbers), a string's stored length is `text + 1`, and `Invalid` is an `UnknownType` error.

## Tests

- Every type round-trips (including `i32::MIN + 1`, an empty string and a string with accents and an emoji), and every NULL comes back as a NULL of the same type.
- The exact bytes: `0x01020304` as `[4, 3, 2, 1]`, a NULL integer as `i32::MIN`'s bytes, a NULL string as `u32::MAX`, and `"abc"` as `4, 0, 0, 0, a, b, c, 0`.
- Reading ignores the bytes after the value, and a shorter type reads a prefix.

## Syntax and methods

```rust
storage[..4].copy_from_slice(&v.to_le_bytes());                   // i32 -> 4 little-endian bytes
i32::from_le_bytes(storage[..4].try_into().unwrap())             // &[u8] (len 4) -> i32
f64::to_le_bytes / f64::from_le_bytes                            // the IEEE-754 bits
String::from_utf8_lossy(&storage[4..4 + n]).into_owned()
```

## Notes

**Little-endian, always.** Module 2a already made this decision for pages: every multi-byte number is written with `to_le_bytes` so the file means the same on every machine. Never `transmute` a struct to bytes.

**Why the string length counts the zero byte.** BusTub stores C strings, and its `GetStorageSize` for a `VARCHAR` returns the length *including* the terminator. The format keeps that so a page written by this port is byte-compatible with BusTub's. A Rust `String` has no terminator, so you write one and subtract one when reading.

**Sentinels are a design choice with a bill.** Because NULL is a bit pattern, a column of `INTEGER`s needs no null bitmap and a tuple's fixed part is a plain concatenation. The bill: one value of every type is unusable, and a decimal column cannot store `f64::MIN`. A flag per column (PostgreSQL's null bitmap, one bit per column) costs one bit and loses nothing. Module 3b's tuples will inherit this choice.

## In BusTub

`IntegerType::SerializeTo` ("*reinterpret_cast<int32_t *>(storage) = val.value_.integer_;"), `VarlenType::SerializeTo`/`DeserializeFrom` ("uint32_t len = GetStorageSize(val); if (len == BUSTUB_VALUE_NULL) { memcpy(storage, &len, sizeof(uint32_t)); return; } memcpy(storage, &len, sizeof(uint32_t)); memcpy(storage + sizeof(uint32_t), val.value_.varlen_, len);").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `*reinterpret_cast<int32_t *>(storage) = v;` (alignment and endianness are the machine's) | `storage[..4].copy_from_slice(&v.to_le_bytes())` |
| `memcpy(&len, storage, 4)` | `u32::from_le_bytes(storage[..4].try_into().unwrap())` |
| `new char[len]` + `memcpy` to build a string value | `String::from_utf8_lossy(bytes).into_owned()` |

**Port rule:** `reinterpret_cast` of a byte buffer becomes `from_le_bytes` of a slice; the slice length is checked, so a short buffer is a panic at the right line instead of a read past the end.

## Learn more
- [`to_le_bytes` / `from_le_bytes`](https://doc.rust-lang.org/std/primitive.i32.html#method.from_le_bytes) · [`<[u8; N]>::try_from(&[u8])`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) · [Endianness](https://en.wikipedia.org/wiki/Endianness) · SQLite's [record format](https://www.sqlite.org/fileformat2.html#record_format) (type codes instead of sentinels)

## Performance

Serialising a fixed-size value is one store; deserialising is one load (the compiler turns `from_le_bytes` of a 4-byte slice into a single unaligned `mov` on x86 and ARM). A string costs a copy of its bytes. The `unwrap()` on `try_into` is a length check on a slice you have just made with a constant length, which the compiler removes. The slow paths are the allocations: reading a `Varchar` allocates a `String`, which is why later modules keep tuples as bytes and decode a column only when asked.

**Measure it.** Serialise and deserialise 10 million integers and 10 million 20-byte strings and report the throughput of each.

## Hints

### Write the NULL cases as data, not as code

Each type has a reserved pattern; `Value::integer(i32::MIN)` already becomes a NULL, so for the numeric types `deserialize_from` can just read the number and call the typed constructor. For `serialize_to`, a `Value::Null(t)` writes `t`'s constant. A table of (type, constant) is easier to check than five separate branches.

### Slice with the length you need

`storage[..4]` panics if `storage` is shorter: that is what you want in a bug (a page with too little room). Use a `word(n)` helper so every read states its width once.

### The string length is text + 1

`storage[4..4 + len - 1]` is the text and `storage[4 + len - 1]` the zero byte. An off-by-one here makes every string one character short or long, and the round-trip test with the emoji (four bytes in UTF-8) finds it at once.
