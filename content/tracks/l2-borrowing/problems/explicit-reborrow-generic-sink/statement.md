`emit_all` takes its sink by value, the way std's generic sinks and iterators do. `pipeline` and
`fan_out` want to lend theirs instead, and don't compile. Make `&mut S` and `Box<S>` sinks for every
sink `S`, trait objects included, the way std does for `io::Write` and `Iterator`. Then fix `pipeline`
so it can still use `sink` after lending it.
