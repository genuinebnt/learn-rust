Write the `LendingIterator` trait: like `Iterator`, but `next(&mut self)` returns an item that may borrow
from the iterator itself, through a generic associated type `Item<'a>`. Then implement it:

- `windows_mut(slice, size)`: overlapping `&mut [T]` windows, moving one element at a time (what
  `slice.windows` does, but mutable). Panics if `size` is 0.
- `upper_lines(text)`: each line trimmed and uppercased, written into one `String` buffer that is reused
  for every line.
- `count` works for any lending iterator.
