Implement a generic `Matrix<T>` stored in one `Vec<T>`, row by row. The bounds on each `impl` are already
chosen; notice which operations need which.

- `zeros`, `from_rows` (panics on ragged rows), `transpose`, `rows`, `cols`, `row(r)` and `rows_iter()`.
- `m[(r, c)]` reads and writes an entry, and panics if either index is out of range.
- `a + b` adds element-wise; `&a * &b` is the matrix product. Both panic on mismatched shapes.
