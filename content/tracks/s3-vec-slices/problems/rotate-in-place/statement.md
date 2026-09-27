- `rotate_right(v, k)`: rotate right by `k` using three reversals (the interview version; don't call
  `rotate_left`/`rotate_right` here). `k` may exceed the length, and the slice may be empty.
- `move_item(v, from, to)`: drag-and-drop reordering. Take the element at `from` and put it at index `to`,
  shifting the elements in between by one place. If either index is out of range, do nothing. Only the
  elements between the two positions may move.
- `swap_pairs(v)`: swap each pair of neighbours; an odd last element stays where it is.
