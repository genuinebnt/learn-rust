`Shape: Clone` makes `dyn Shape` impossible (E0038), and `scale_all` calls a `scaled_box` that doesn't
exist. Make both functions work:

- `Vec<Box<dyn Shape>>` must be cloneable, so `snapshot` compiles as written.
- `scaled_box(&self, k) -> Box<dyn Shape>` must work on `dyn Shape`, and `scaled` must keep returning the
  concrete type.
- Shapes defined elsewhere (the tests define one) derive `Clone` and implement only `area`, `name` and
  `scaled`.
