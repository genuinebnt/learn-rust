- `apply_n` and `apply_n_dyn` apply `f` to `start`, `n` times: one generic, one through `&mut dyn FnMut`.
- `Pipeline` stores steps of different closure types and threads a value through them in push order.
  Steps may mutate what they capture, may borrow local variables (the `'a`), and a pipeline must be
  movable to another thread. Choose the field type.
