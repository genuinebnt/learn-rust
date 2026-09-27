`Report` only holds a `Vec`. Make it hold any collection `C` (a `Vec`, an array, a `BTreeSet`, a `VecDeque`,
an `Option`, or the tests' own `Evens`) and print whenever iterating `&C` yields printable items.

Printing must not consume, clone or copy the rows: `rows()` still returns the collection afterwards, and
`Evens` isn't `Clone`. The output format stays the same.
