`Matrix<T, R, C>` stores `[[T; C]; R]`, so multiplying a 2×3 by a 2×3 is a type error, not a panic. Fill in
the methods and operators; the signatures and bounds are given.

- `get(r, c)` is `None` out of range.
- `transpose` must **move** the elements: it needs nothing from `T`, and the tests transpose a type that
  can't be cloned.
- `identity(one)` exists only for square matrices; off-diagonal cells are `T::default()`.
- `+` is element-wise; `*` is the matrix product.
