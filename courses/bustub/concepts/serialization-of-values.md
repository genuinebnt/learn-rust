---
title: Serialising values: bytes, byte order and NULL
summary: Fixed-width little-endian numbers, a length-prefixed string, NULL as a reserved pattern versus a null bitmap, and round-trip testing; the contract tuples and pages are built on.
minutes: 9
---
A value in memory is a Rust enum; a value in a page is a run of bytes. **Serialising** turns the first into the second and **deserialising** reverses it. The two functions must be exact inverses, and the byte layout is a promise to every future reader of the file: change it and old files are unreadable.

## The decisions every format makes

| question | BusTub's answer |
|---|---|
| byte order of numbers | little-endian (`to_le_bytes`) |
| width of an integer | its type's width: 1, 2, 4 or 8 bytes |
| a boolean | one byte, 0 or 1 |
| a decimal | the 8 bytes of the IEEE-754 double |
| a string | a 4-byte length, then the bytes (and a terminating zero, counted in the length) |
| NULL | a reserved pattern: `i32::MIN` for an integer, length `u32::MAX` for a string |

## Two ways to store NULL

1. **A reserved value** (BusTub). No extra space, no extra code to read a column, but one legal value per type is lost, and the sentinel must never be produced by accident.
2. **A null bitmap** (PostgreSQL: one bit per column in the tuple header; the null columns take *no space*) or a **flag byte** per value. Every value is usable; a reader checks the bitmap first.

Either way the in-memory form is the same: `Value::Null(type)` (or `Option<T>`).

## Variable-length data

A string cannot sit at a fixed offset, so formats put a **length first** (`| u32 length | bytes |`) and read the length to know where the next field starts. The length counts bytes, not characters: UTF-8 characters are 1 to 4 bytes. Putting the length first also makes it easy to skip a value without decoding it.

## Testing a codec

Two tests find nearly every bug: **round-trip** (`deserialize(serialize(v)) == v` for every kind of value, at the edges: smallest, largest, empty, NULL, multi-byte text) and **golden bytes** (the exact bytes of a known value, which pins the byte order and the layout so a refactor cannot change the format silently).

## C++ comparison

| C / C++ | Rust |
|---|---|
| `*reinterpret_cast<int32_t *>(storage) = v;` | `storage[..4].copy_from_slice(&v.to_le_bytes())` |
| `memcpy(&v, storage, 4)` | `i32::from_le_bytes(storage[..4].try_into().unwrap())` |
| `char *` plus `len` | `&[u8]` / `&mut [u8]`, bounds-checked |
| `struct __attribute__((packed))` cast over a buffer | explicit offsets; no alignment assumptions |

## In real code

### Using it: a codec with golden bytes and a round trip

```rust test
#[derive(Clone, Debug, PartialEq)]
enum V { Null(Kind), Bool(bool), Int(i32), Big(i64), Dec(f64), Text(String) }
#[derive(Clone, Copy, Debug, PartialEq)]
enum Kind { Bool, Int, Big, Dec, Text }

impl V {
    fn encoded_len(&self) -> usize {
        match self {
            V::Bool(_) => 1,
            V::Int(_) => 4,
            V::Big(_) | V::Dec(_) => 8,
            V::Text(s) => 4 + s.len() + 1,
            V::Null(Kind::Text) => 4,
            V::Null(Kind::Bool) => 1,
            V::Null(Kind::Int) => 4,
            V::Null(Kind::Big) | V::Null(Kind::Dec) => 8,
        }
    }
    fn write(&self, out: &mut [u8]) {
        match self {
            V::Bool(b) => out[0] = *b as u8,
            V::Int(i) => out[..4].copy_from_slice(&i.to_le_bytes()),
            V::Big(i) => out[..8].copy_from_slice(&i.to_le_bytes()),
            V::Dec(d) => out[..8].copy_from_slice(&d.to_le_bytes()),
            V::Text(s) => {
                out[..4].copy_from_slice(&(s.len() as u32 + 1).to_le_bytes());       // the length counts the zero byte
                out[4..4 + s.len()].copy_from_slice(s.as_bytes());
                out[4 + s.len()] = 0;
            }
            V::Null(Kind::Bool) => out[0] = i8::MIN as u8,
            V::Null(Kind::Int) => out[..4].copy_from_slice(&i32::MIN.to_le_bytes()),
            V::Null(Kind::Big) => out[..8].copy_from_slice(&i64::MIN.to_le_bytes()),
            V::Null(Kind::Dec) => out[..8].copy_from_slice(&f64::MIN.to_le_bytes()),
            V::Null(Kind::Text) => out[..4].copy_from_slice(&u32::MAX.to_le_bytes()),
        }
    }
    fn read(kind: Kind, b: &[u8]) -> V {
        match kind {
            Kind::Bool => if b[0] as i8 == i8::MIN { V::Null(kind) } else { V::Bool(b[0] != 0) },
            Kind::Int => { let v = i32::from_le_bytes(b[..4].try_into().unwrap()); if v == i32::MIN { V::Null(kind) } else { V::Int(v) } }
            Kind::Big => { let v = i64::from_le_bytes(b[..8].try_into().unwrap()); if v == i64::MIN { V::Null(kind) } else { V::Big(v) } }
            Kind::Dec => { let v = f64::from_le_bytes(b[..8].try_into().unwrap()); if v == f64::MIN { V::Null(kind) } else { V::Dec(v) } }
            Kind::Text => {
                let len = u32::from_le_bytes(b[..4].try_into().unwrap());
                if len == u32::MAX { V::Null(kind) } else { V::Text(String::from_utf8_lossy(&b[4..4 + len as usize - 1]).into_owned()) }
            }
        }
    }
    fn kind(&self) -> Kind {
        match self { V::Null(k) => *k, V::Bool(_) => Kind::Bool, V::Int(_) => Kind::Int, V::Big(_) => Kind::Big, V::Dec(_) => Kind::Dec, V::Text(_) => Kind::Text }
    }
}

#[test]
fn golden_bytes_pin_the_format() {
    let mut b = [0u8; 8];
    V::Int(0x0102_0304).write(&mut b);
    assert_eq!(&b[..4], &[4, 3, 2, 1], "little-endian: the low byte first");
    V::Null(Kind::Int).write(&mut b);
    assert_eq!(&b[..4], &i32::MIN.to_le_bytes());
    let mut t = vec![0u8; V::Text("abc".into()).encoded_len()];
    V::Text("abc".into()).write(&mut t);
    assert_eq!(t, vec![4, 0, 0, 0, b'a', b'b', b'c', 0]);
    let mut n = [0u8; 4];
    V::Null(Kind::Text).write(&mut n);
    assert_eq!(n, [255, 255, 255, 255]);
}

#[test]
fn every_value_round_trips() {
    for v in [V::Bool(true), V::Bool(false), V::Int(i32::MAX), V::Int(i32::MIN + 1), V::Big(-1), V::Dec(0.1), V::Text(String::new()), V::Text("héllo 🥰".into()),
              V::Null(Kind::Bool), V::Null(Kind::Int), V::Null(Kind::Big), V::Null(Kind::Dec), V::Null(Kind::Text)] {
        let mut buf = vec![0xEEu8; v.encoded_len() + 2];     // extra bytes must not matter
        v.write(&mut buf);
        assert_eq!(V::read(v.kind(), &buf), v, "{v:?}");
    }
}
```

```rust test
/// The other way to store NULL: a bitmap in front of the values; null columns take no space.
fn encode_row(cols: &[Option<i32>]) -> Vec<u8> {
    let mut bitmap = vec![0u8; cols.len().div_ceil(8)];
    let mut body = vec![];
    for (i, c) in cols.iter().enumerate() {
        match c {
            Some(v) => { bitmap[i / 8] |= 1 << (i % 8); body.extend_from_slice(&v.to_le_bytes()); }   // bit set = present
            None => {}
        }
    }
    [bitmap, body].concat()
}

fn decode_row(bytes: &[u8], n: usize) -> Vec<Option<i32>> {
    let bitmap_len = n.div_ceil(8);
    let mut at = bitmap_len;
    (0..n).map(|i| {
        if bytes[i / 8] & (1 << (i % 8)) != 0 {
            let v = i32::from_le_bytes(bytes[at..at + 4].try_into().unwrap());
            at += 4;
            Some(v)
        } else { None }
    }).collect()
}

#[test]
fn a_null_bitmap_loses_no_values_and_nulls_take_no_room() {
    let row = [Some(i32::MIN), None, Some(7), None, None, Some(-1)];           // i32::MIN is a legal value here
    let bytes = encode_row(&row);
    assert_eq!(bytes.len(), 1 + 3 * 4, "one bitmap byte and three present values");
    assert_eq!(decode_row(&bytes, row.len()), row.to_vec());
    let all_null = [None, None, None];
    assert_eq!(encode_row(&all_null).len(), 1);
    assert_eq!(decode_row(&encode_row(&all_null), 3), all_null.to_vec());
}
```

### In the exercises

- **3a-06:** `serialize_to`, `deserialize_from` and `storage_size` are the first test's `write`, `read` and `encoded_len`; the stage's tests are its golden bytes and its round trip.
- **Module 3b:** a tuple is its values' encodings one after another (fixed-size fields inline, strings by offset), so the codec is the base of `Tuple::new` and `get_value`.
- **The bitmap alternative** is what you would add if the reserved-number trade-off (stage 2) bothered you.

### Where it is used

- **Databases**: PostgreSQL's heap tuple header has a null bitmap; SQLite's record format has a type code per column (serial type 0 is NULL); MySQL InnoDB rows have a null bitmap too.
- **Wire and file formats**: Protocol Buffers (varints, length-prefixed fields), Apache Arrow (a validity bitmap per column), Avro, MessagePack, Parquet.
- **Rust**: `bincode`, `postcard` and `serde` serialisers do this generically; `byteorder` and `zerocopy` are the helper crates for hand-written formats.
