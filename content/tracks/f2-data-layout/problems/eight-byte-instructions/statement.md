A JIT's interpreter tier stores a function as a `Vec<Inst>`. Today `Inst` is just `Op`: **32 bytes**,
because one rare variant carries an `i64` and another a `Vec` of jump targets. The dispatch loop
streams through instructions, so every byte of `Inst` costs cache space.

Make `Inst` **8 bytes** (and `Option<Inst>` too). The front end still hands `push` an `Op`, and
`run` behaves exactly as before: registers start at 0, arithmetic wraps, `BrTable` falls back to
`default` when the index is negative or out of range, and `run` returns `None` when control runs
off the end or `fuel` instructions have executed without a `Ret`.
