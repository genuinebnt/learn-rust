Byte offsets are what `str` methods return; people count characters. Write the conversions an error
reporter needs:

- `line_col(src, at)`: the 1-based line and column of byte offset `at`, with the column counted in
  characters. `at == src.len()` is valid (the end of the text). Return `None` when `at` is past the end or
  falls inside a character. Lines end at `\n`; a `\r` is an ordinary character.
- `char_to_byte(s, n)`: the byte offset where character `n` (0-based) starts, `s.len()` when `n` equals
  the number of characters, and `None` beyond that.
- `find_all(s, needle)`: every non-overlapping occurrence of the non-empty `needle`, left to right, as
  `(byte offset, char offset)`. It must stay linear in `s.len()`.
