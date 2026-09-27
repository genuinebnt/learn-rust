Write the leaf page of a B-tree, as SQLite and PostgreSQL lay it out: **everything in one
`[u8; 4096]`**, so `size_of::<Page>()` is 4096 and nothing allocates, not even `compact`.

The format (all integers `u16` little-endian):

- **Header**, bytes 0..8: cell count `n`; `cell_start`, where the cell area begins (4096 when empty);
  `fragmented`, bytes of dead cells inside the cell area; then 0.
- **Slot array** from byte 8: slot `i` is (cell offset, cell length) at `8 + 4i`, sorted by key
  (bytewise).
- **Cells**, growing down from the end: key length, key bytes, value bytes. A new cell goes right
  below `cell_start`.

`insert` adds a key or replaces its value (the old cell becomes fragmented). If the slot array and
the cells wouldn't fit even counting fragmented bytes, it returns `Err(PageFull)` and changes nothing;
if they fit but the contiguous gap is too small, it compacts first. `delete` removes the slot (later
slots shift down) and fragments the cell. `compact` rewrites the cell area with the cells packed
against the end in **slot order** (slot 0's cell ends at 4096), `fragmented` = 0, and the free gap
zeroed. `free_space` counts the gap plus fragmented bytes; `get` and `iter` borrow from the page.
