None of these types derive anything, so the code below them and the tests don't compile. Give each type
what it should have:

- `Point` and `Pixel` are plain data: they should be `Copy`, and comparable and printable with `{:?}`.
- `Sprite` owns a `String`: clonable (a deep copy), comparable, printable.
- `Id<T>` should be `Copy`, comparable with `==`, usable as a `HashSet` key, and print as `Id(7)`, **for
  every `T`**, including a type with no derives at all.
