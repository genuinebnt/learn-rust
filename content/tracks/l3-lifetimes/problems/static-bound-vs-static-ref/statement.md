Write `impl Extensions`: a map holding at most one value per type, keyed by `TypeId`.

- `new()`, and `len()`: how many values it holds.
- `insert(value)`: stores it, replacing and returning the previous value of the same type, by value.
- `get::<T>()` and `get_mut::<T>()`: the value of type `T`, borrowed.
- `remove::<T>()`: takes the value of type `T` out, by value.

Then fix `remember`, which doesn't compile. `intern_forever` is correct: read it as the other half
of the lesson.
