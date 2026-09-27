Implement `next`, `size_hint` and `next_back` for `StepMut`, which yields every `step`-th element of a
slice as `&mut`. The items must be able to live together (the tests collect them all and then write
through each), and there's no `unsafe`.
