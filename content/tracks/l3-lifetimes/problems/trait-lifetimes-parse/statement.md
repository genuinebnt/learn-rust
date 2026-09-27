`Parse<'a>` is modelled on serde's `Deserialize<'de>`: the lifetime lets a parsed value borrow from the
text. Implement it for `&'a str` (the field, trimmed) and for `Pair<'a>` (`key=value`, both parts
trimmed, `None` without an `=`), so that `fields` can return borrowed values. Then fix `read_owned`,
whose bound can't work: it parses a `String` it owns and drops.
