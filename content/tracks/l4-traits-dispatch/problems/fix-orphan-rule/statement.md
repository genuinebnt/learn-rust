`impl Display for Vec<Point>` breaks the orphan rule (E0117). Replace it with a newtype
`pub struct Path(pub Vec<Point>)` that prints the same way.

Callers must still use a path like the `Vec`: `path.len()`, `path[0]`, `path.iter()`, `path.push(p)`, and
`length(&path)`. They build one with `Path::from(vec)` or by `collect()`ing points.
