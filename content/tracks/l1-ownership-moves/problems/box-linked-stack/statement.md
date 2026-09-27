Write a stack as a linked list of `Box`ed nodes. Nodes are moved, never copied or reallocated:

- `push`, `pop`, `peek` and `len` as usual.
- `reverse` reverses the stack in place, and `move_top_to` moves the top node onto another stack. Both
  reuse the existing boxes: **no allocation at all** (the tests count them).
- `into_vec` returns the values top first.
- Dropping a stack of a million nodes must not overflow the thread's stack.
