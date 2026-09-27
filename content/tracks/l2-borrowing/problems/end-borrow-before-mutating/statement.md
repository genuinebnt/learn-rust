`intern` takes `&mut self` and returns a `&str` into the interner. `intern_all` and `intern_edges` keep
those `&str`s while calling `intern` again, and neither compiles. Fix both functions without changing
`Interner` and without copying any name: the `&str`s they return must be the interner's stored names.
