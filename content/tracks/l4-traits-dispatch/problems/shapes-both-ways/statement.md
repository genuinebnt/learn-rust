Two bugs:

- The tests pass `Vec<Box<dyn Shape>>`, `Vec<&dyn Shape>` and `Vec<&Circle>` to the generic functions.
  None of that compiles (E0277).
- `largest` returns the last of several equally large shapes, not the first.

Fix both without changing any function's signature.
