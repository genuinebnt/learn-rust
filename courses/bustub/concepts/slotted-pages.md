---
title: Slotted pages: stable addresses in a page that changes
summary: The page layout of nearly every row store: a slot array from the front, records from the back, record ids that survive inserts and deletes, and how free space is computed.
minutes: 9
---
A database page (8 KiB here) holds many records of different sizes, and records come and go. The question every row store must answer: *how do you address a record so that the address stays valid as the page changes?* The answer, from the 1970s and still in use, is a **slotted page**.

```svg
caption: A slotted page. The slot array (small, fixed-size entries) grows from the front; the records (variable-size) grow from the back; free space is the gap between them. A record is addressed by its slot number, so its bytes can move without anyone's address changing. Deleting sets a flag in the slot.
<svg viewBox="0 0 760 230" role="img" aria-label="A page with a header, three slots growing right, free space and three records growing left">
<defs><marker id="sp-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="box" x="20" y="60" width="70" height="44" rx="2"/><text class="mid dim sm" x="55" y="86">header</text>
<rect class="blue" x="92" y="60" width="52" height="44" rx="2"/><text class="mid t-b sm" x="118" y="86">slot 0</text>
<rect class="blue" x="146" y="60" width="52" height="44" rx="2"/><text class="mid t-b sm" x="172" y="86">slot 1</text>
<rect class="blue" x="200" y="60" width="52" height="44" rx="2"/><text class="mid t-b sm" x="226" y="86">slot 2</text>
<rect class="never" x="254" y="60" width="230" height="44" rx="2"/><text class="mid dim" x="369" y="86">free space</text>
<rect class="live" x="486" y="60" width="60" height="44" rx="2"/><text class="mid fg sm" x="516" y="86">tuple 2</text>
<rect class="live" x="548" y="60" width="90" height="44" rx="2"/><text class="mid fg sm" x="593" y="86">tuple 1</text>
<rect class="live" x="640" y="60" width="100" height="44" rx="2"/><text class="mid fg sm" x="690" y="86">tuple 0</text>
<path class="ln-b" d="M118 60 C118 20 690 20 690 58" marker-end="url(#sp-a)"/><text class="t-b sm" x="360" y="30">slot 0 → offset and size of tuple 0</text>
<path class="ln" d="M226 104 C226 150 516 150 516 106" marker-end="url(#sp-a)"/><text class="dim sm" x="300" y="170">slot 2 → tuple 2</text>
<text class="dim sm" x="20" y="205">grows →</text><text class="dim sm" x="690" y="205" style="text-anchor:end">← grows</text>
</svg>
```

## What is in a slot

For each record: its **offset** in the page, its **size**, and (here) a little metadata (a timestamp and a deleted flag). The slot array is a plain array of fixed-size entries, so slot `i` is at `header + i * slot_size`.

## Operations

| operation | what it does | cost |
|---|---|---|
| **insert** | new slot at the end of the array; record just below the lowest record; fails if they would overlap | O(1) |
| **read** `(page, slot)` | read the slot, then the bytes at its offset | O(1) |
| **delete** | set the slot's deleted flag (the bytes stay) | O(1) |
| **update in place** | overwrite the bytes; only if the new record has the same size | O(size) |
| **compact** | slide records together, rewrite the slots' offsets; slot numbers do not change | O(page) |

**Free space** is `record_area_start - slot_array_end`, and an insert needs `record_size + slot_size` of it, because the new slot also takes room.

## Why the indirection is worth a slot

If addresses were byte offsets, compacting the page would change them, and every index entry pointing at a record would be wrong. With slots, an index stores `(page_id, slot_number)`: a **record id**. The page may be compacted, records moved, the page even rewritten: the slot number is stable for the record's lifetime.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `char page_[8192]; struct TupleInfo { uint16_t offset, size; ... } tuple_info_[0];` | a view over `&mut [u8]` with `slot_at(i)` and decode/encode functions |
| `tuple_info_[n] = {offset, size, meta}` through a cast | `set_slot(n, offset, size, &meta)` writing little-endian fields |
| `size_t room = a - b;` (wraps if `b > a`) | `a.checked_sub(b)` |

## In real code

### Using it: a slotted page in a `Vec<u8>`

```rust test
const PAGE: usize = 128;          // a small page keeps the arithmetic readable
const HEADER: usize = 2;          // num_slots: u16
const SLOT: usize = 4;            // offset: u16, size: u16

struct Page { bytes: [u8; PAGE] }

impl Page {
    fn new() -> Page { Page { bytes: [0; PAGE] } }
    fn num_slots(&self) -> usize { u16::from_le_bytes([self.bytes[0], self.bytes[1]]) as usize }
    fn slot(&self, i: usize) -> (usize, usize) {
        let at = HEADER + i * SLOT;
        (u16::from_le_bytes([self.bytes[at], self.bytes[at + 1]]) as usize, u16::from_le_bytes([self.bytes[at + 2], self.bytes[at + 3]]) as usize)
    }
    /// Where a record of `len` bytes would start, if it fits.
    fn next_offset(&self, len: usize) -> Option<usize> {
        let n = self.num_slots();
        let end = if n > 0 { self.slot(n - 1).0 } else { PAGE };
        let start = end.checked_sub(len)?;
        (start >= HEADER + SLOT * (n + 1)).then_some(start)
    }
    fn insert(&mut self, record: &[u8]) -> Option<usize> {
        let start = self.next_offset(record.len())?;
        let n = self.num_slots();
        let at = HEADER + n * SLOT;
        self.bytes[at..at + 2].copy_from_slice(&(start as u16).to_le_bytes());
        self.bytes[at + 2..at + 4].copy_from_slice(&(record.len() as u16).to_le_bytes());
        self.bytes[start..start + record.len()].copy_from_slice(record);
        self.bytes[..2].copy_from_slice(&(n as u16 + 1).to_le_bytes());
        Some(n)
    }
    fn get(&self, slot: usize) -> Option<&[u8]> {
        (slot < self.num_slots()).then(|| { let (o, s) = self.slot(slot); &self.bytes[o..o + s] })
    }
}

#[test]
fn records_are_addressed_by_slot_and_grow_from_the_back() {
    let mut p = Page::new();
    assert_eq!(p.insert(b"first"), Some(0));
    assert_eq!(p.insert(b"second!"), Some(1));
    assert_eq!(p.slot(0), (PAGE - 5, 5));
    assert_eq!(p.slot(1), (PAGE - 5 - 7, 7));
    assert_eq!(p.get(1), Some(&b"second!"[..]));
    assert_eq!(p.get(2), None);
}

#[test]
fn the_page_is_full_when_the_slots_and_the_records_would_meet() {
    let mut p = Page::new();
    let mut n = 0;
    while p.insert(&[n as u8; 10]).is_some() { n += 1; }
    // 2 + n * (4 + 10) <= 128  =>  n = 9
    assert_eq!(n, 9);
    assert_eq!(p.insert(&[0; 10]), None, "full");
    assert_eq!(p.insert(&[0; 1]), None, "even one byte needs a slot too: 2 + 9*14 = 128");
    for i in 0..9 { assert_eq!(p.get(i).unwrap(), &[i as u8; 10][..]); }
    assert_eq!(Page::new().insert(&[0; 200]), None, "a record bigger than the page: no underflow, just None");
}
```

```rust test
/// Compaction: records slide towards the back, slots keep their numbers (only the offsets change).
fn compact(slots: &mut Vec<(usize, usize)>, bytes: &mut [u8], page: usize) {
    // process records from the highest offset to the lowest so each moves back without overwriting the next
    let mut order: Vec<usize> = (0..slots.len()).collect();
    order.sort_by_key(|&i| std::cmp::Reverse(slots[i].0));
    let mut end = page;
    for i in order {
        let (off, len) = slots[i];
        let new = end - len;
        bytes.copy_within(off..off + len, new);        // memmove: ranges may overlap
        slots[i].0 = new;
        end = new;
    }
}

#[test]
fn compacting_changes_offsets_but_not_slot_numbers() {
    let mut bytes = vec![0u8; 64];
    bytes[56..64].copy_from_slice(b"AAAAAAAA");        // slot 0
    bytes[40..46].copy_from_slice(b"BBBBBB");          // slot 1 (there is a 10-byte hole between 46..56)
    bytes[30..34].copy_from_slice(b"CCCC");            // slot 2 (and another hole)
    let mut slots = vec![(56, 8), (40, 6), (30, 4)];
    compact(&mut slots, &mut bytes, 64);
    assert_eq!(slots, vec![(56, 8), (50, 6), (46, 4)]);
    assert_eq!(&bytes[50..56], b"BBBBBB");
    assert_eq!(&bytes[46..50], b"CCCC");
    assert_eq!(&bytes[56..64], b"AAAAAAAA", "slot 0 still names record A: the address survived the move");
}
```

### In the exercises

- **3b-05:** `get_next_tuple_offset` is `next_offset` (a `checked_sub` and the slot-array comparison) and `insert_tuple` is `insert`; the "full when they meet" test is the second test.
- **3b-06:** `get_tuple` and `update_tuple_meta` index the slot array; deleting is a flag, not a compaction (BusTub never compacts).
- **Module 3c:** `Rid(page_id, slot)` is the record id; the table heap and the iterator walk pages and slots.

### Where it is used

- **PostgreSQL**: heap pages have an array of *line pointers* (4 bytes each) at the front and tuples from the back; an index entry's `ctid` is `(block, line pointer)`; `VACUUM` compacts a page without changing line pointer numbers.
- **SQLite**: a B-tree page has a *cell pointer array* from the front and cells from the back, and `defragment` compacts them.
- **MySQL InnoDB** index pages and **Oracle** blocks use a page directory with the same purpose.
- **Memory allocators** use the same shape (a handle table plus a compacting heap) when objects must be relocatable: "handles instead of pointers", like the generational arenas of module 1.
