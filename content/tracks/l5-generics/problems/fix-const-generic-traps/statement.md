`Ring<T, N>` is a fixed-capacity ring buffer and `concat` joins two arrays. Neither compiles, and neither
should need anything from `T`: the tests use `String` and a `Token` type with no derives.

- `Ring::new()` must work for any `T`, and `N` may be `0` (a zero-capacity ring hands every pushed item
  straight back).
- `concat` returns `[T; C]`, where the caller picks `C` (usually by annotating the result) and it must equal
  `A + B`.

Keep the storage in arrays.
