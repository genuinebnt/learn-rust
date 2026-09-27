- `join_words(words, sep)`: `words` with `sep` between them, without `join`, `concat`, `collect` or
  `fold`, in **one** allocation of exactly the final size (an empty result allocates nothing).
- `squeeze(s)`: drop leading and trailing whitespace, and in each inner run of whitespace keep only its
  first character (`"a \t b"` → `"a b"`, `"a\t b"` → `"a\tb"`). In place, no allocation.
- `pop_line(buf)`: `buf` is a network read buffer. Remove the first complete line and return it
  without its `\n` or `\r\n`; the rest stays in `buf`. If `buf` holds no `\n` yet, return `None`
  and leave `buf` as it is.
