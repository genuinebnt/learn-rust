---
title: Tuple layout: a fixed part, a variable part and offsets between them
summary: Why rows are laid out as fixed-size slots plus a heap of variable-size data, how a column is found in constant time, and how the same trick shows up in PostgreSQL, SQLite and Rust's own strings.
minutes: 9
---
A row has columns of different sizes: a 4-byte integer, a 20-byte name, an 8-byte timestamp. If you store them one after another, finding column 7 means measuring columns 0 to 6. A database reads column 7 of millions of rows, so it wants that to be one addition. The answer is to split the row into two parts.

```text
fixed part (same shape for every row of the table)              variable part (differs per row)
| id: INT (4) | name: offset (4) | score: BIGINT (8) | tag: offset (4) | "Ada" len+bytes | "x" len+bytes |
0             4                  8                   16                20
                 |                                         |            ^                    ^
                 +----------> points at ------------------------------- 20                  27
```

- The **fixed part** has one slot per column, in column order. A fixed-size column (integer, boolean, decimal) stores its value *in its slot*. A variable-size column (a string) stores an **offset**: where in the row its bytes begin.
- The **variable part** holds the variable-size values, each as `length + bytes`.
- A column's position is the **schema's offset** for it: computed once per table, not per row. Reading a fixed column is `row[offset..]`; reading a string is one more hop: `row[row[offset..]..]`.

## What this buys, and costs

| property | result |
|---|---|
| read any column | O(1): an addition and a load (plus one hop for a string) |
| fixed part size | identical for every row: a row's fixed part is `schema.length()` bytes |
| a row's total size | fixed part + sum of its strings (known before writing: size first, then write) |
| change a string to another length | the row changes size (it cannot be updated in place) |
| NULL | a reserved pattern (here) or a bit in a header (PostgreSQL): no extra space per column |

Notice that a string's slot is **4 bytes whatever the string**. The fixed part must stay fixed; the offset is a fixed-size stand-in for a variable-size value.

## Rows and columns

This is a **row store** (N-ary storage model): all columns of a row are adjacent. Analytical databases use **column stores**: all values of one column adjacent, so `SUM(price)` reads one array. A row store is better for `INSERT`, `UPDATE` and "fetch one row"; a column store for scans of a few columns. BusTub is a row store.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `struct { int32_t id; char name[20]; }` (a fixed row; wastes space on short names) | fixed part + offset + heap: pay only for the string's real length |
| `*reinterpret_cast<int32_t *>(data + col.GetOffset())` | `i32::from_le_bytes(data[off..off + 4].try_into().unwrap())` |
| flexible array member / trailing data after a header struct | a byte buffer and explicit offsets |

## In real code

### Using it: a tiny row codec with a fixed part and a heap

```rust test
#[derive(Clone, Copy, Debug, PartialEq)]
enum Ty { Int, Text }

#[derive(Clone, Debug, PartialEq)]
enum Val { Int(i32), Text(String) }

/// Offsets of each column in the fixed part (a text column takes a 4-byte offset slot), and the fixed part's size.
fn layout(schema: &[Ty]) -> (Vec<usize>, usize) {
    let mut offsets = vec![];
    let mut at = 0;
    for t in schema {
        offsets.push(at);
        at += 4;                               // an Int is 4 bytes; a Text slot is a 4-byte offset
    }
    (offsets, at)
}

fn encode(schema: &[Ty], row: &[Val]) -> Vec<u8> {
    let (offsets, fixed) = layout(schema);
    let size = fixed + row.iter().map(|v| if let Val::Text(s) = v { 4 + s.len() } else { 0 }).sum::<usize>();   // size first
    let mut out = vec![0u8; size];
    let mut heap = fixed;
    for (v, &off) in row.iter().zip(&offsets) {
        match v {
            Val::Int(i) => out[off..off + 4].copy_from_slice(&i.to_le_bytes()),
            Val::Text(s) => {
                out[off..off + 4].copy_from_slice(&(heap as u32).to_le_bytes());          // the slot says where
                out[heap..heap + 4].copy_from_slice(&(s.len() as u32).to_le_bytes());      // length, then bytes
                out[heap + 4..heap + 4 + s.len()].copy_from_slice(s.as_bytes());
                heap += 4 + s.len();
            }
        }
    }
    out
}

fn column(schema: &[Ty], bytes: &[u8], idx: usize) -> Val {          // O(1): no walking over earlier columns
    let (offsets, _) = layout(schema);
    let off = offsets[idx];
    match schema[idx] {
        Ty::Int => Val::Int(i32::from_le_bytes(bytes[off..off + 4].try_into().unwrap())),
        Ty::Text => {
            let at = u32::from_le_bytes(bytes[off..off + 4].try_into().unwrap()) as usize;      // one hop
            let len = u32::from_le_bytes(bytes[at..at + 4].try_into().unwrap()) as usize;
            Val::Text(String::from_utf8(bytes[at + 4..at + 4 + len].to_vec()).unwrap())
        }
    }
}

#[test]
fn the_fixed_part_holds_ints_and_offsets_and_the_heap_holds_the_text() {
    let schema = [Ty::Int, Ty::Text, Ty::Int, Ty::Text];
    let row = [Val::Int(7), Val::Text("Ada".into()), Val::Int(-1), Val::Text("x".into())];
    let bytes = encode(&schema, &row);
    assert_eq!(layout(&schema), (vec![0, 4, 8, 12], 16));
    assert_eq!(bytes.len(), 16 + (4 + 3) + (4 + 1));
    assert_eq!(&bytes[4..8], &16u32.to_le_bytes(), "the first string starts right after the fixed part");
    assert_eq!(&bytes[12..16], &23u32.to_le_bytes(), "the second after the first: 16 + 7");
    for (i, v) in row.iter().enumerate() {
        assert_eq!(&column(&schema, &bytes, i), v);
    }
}

#[test]
fn two_rows_of_one_schema_have_the_same_fixed_part_size_and_different_totals() {
    let schema = [Ty::Int, Ty::Text];
    let short = encode(&schema, &[Val::Int(1), Val::Text("a".into())]);
    let long = encode(&schema, &[Val::Int(1), Val::Text("a much longer string".into())]);
    assert_eq!(layout(&schema).1, 8);
    assert_eq!((short.len(), long.len()), (8 + 5, 8 + 4 + 20));
    assert_eq!(column(&schema, &long, 1), Val::Text("a much longer string".into()), "the same offset arithmetic works for both");
}
```

```rust test
#[test]
fn rusts_own_strings_use_the_same_idea() {
    // a String is a fixed-size header (pointer, capacity, length) pointing at variable-size bytes elsewhere
    assert_eq!(std::mem::size_of::<String>(), 3 * std::mem::size_of::<usize>());
    let short = String::from("a");
    let long = "a".repeat(1000);
    assert_eq!(std::mem::size_of_val(&short), std::mem::size_of_val(&long), "the handle has one size whatever the text");
    assert_eq!(short.len() + long.len(), 1001);

    // a Vec<String> is an array of fixed-size slots (the "fixed part"): element i is found by arithmetic
    let rows: Vec<String> = vec!["ab".into(), "cdefgh".into(), "i".into()];
    let base = rows.as_ptr() as usize;
    let third = &rows[2] as *const String as usize;
    assert_eq!(third - base, 2 * std::mem::size_of::<String>());
}
```

### In the exercises

- **3b-02:** `Schema::new` is `layout`: a running offset, 4 bytes for a text slot, and the fixed length at the end.
- **3b-03:** `Tuple::new` is `encode`: size first, then write the fixed values and the heap, slot by slot.
- **3b-04:** `Tuple::get_value` is `column`: the offset from the schema, one hop for a `VARCHAR`.
- **Module 3b executors**: projections and joins build new tuples with new schemas, so every operator that outputs rows does `encode`.

### Where it is used

- **PostgreSQL**: a heap tuple has a fixed header, then attributes laid out by the schema's alignment rules; variable-length attributes (`varlena`) carry a length word; an attribute's offset is cached across rows when all earlier ones are fixed-size.
- **SQLite**: a record is a header of per-column type codes, then the column bodies; offsets are found by summing sizes from the header.
- **Columnar formats** (Apache Arrow, Parquet): a string column is an array of offsets plus one data buffer: exactly this layout, one column at a time.
- **Rust**: `String`/`Vec` handles, `Box<str>`, and `[(offset, len)]` tables into one big buffer (an interner, a rope, an arena) are the same trade.
