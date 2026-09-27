`word_counts` counts words (split on Unicode whitespace, case-sensitive) and returns them most frequent
first, ties in byte order. It's generic over `R: Read`, so its whole body is compiled again for every reader
type a program uses.

- Move the work into a **non-generic** `pub fn word_counts_dyn(reader: &mut dyn Read)` with the same
  result type, and make `word_counts` a one-line forwarder. The tests use `word_counts_dyn` as a plain `fn`
  pointer.
- It also breaks on readers that hand out a few bytes at a time or return `ErrorKind::Interrupted` (which
  means "retry"). Fix those. Input that isn't UTF-8 fails with `ErrorKind::InvalidData`; other read errors
  are passed on.
