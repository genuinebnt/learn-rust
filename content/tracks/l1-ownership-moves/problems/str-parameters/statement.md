These signatures only accept owned `String`s in one exact container, so the tests don't compile. Change
each signature so callers can pass what they have, then write the bodies:

- `first_word` and `extension` take a literal or a `&String`, and return **slices of their input**, with
  no allocation.
- `extension`: the text after the last `.` of the file name (the part after the last `/`), unless that
  dot is the name's first character. `"a/b.tar.gz"` → `"gz"`, `"x."` → `""`, `".bashrc"` and
  `"dir.d/file"` → none.
- `join_nonempty` takes a slice of `&str`, of `String`, or of anything else that can be read as a `str`.
- `count_word` takes **any iterator** of string-likes, owned or borrowed: a `Vec<String>`, a `&Vec<String>`,
  or `text.split_whitespace()`.
