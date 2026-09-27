- `escape_html(s)`: escape `&`, `<`, `>`, `"` and `'` as `&amp;`, `&lt;`, `&gt;`, `&quot;` and `&#39;`.
  When there's nothing to escape, return `s` borrowed, without allocating.
- `escape_bytes(bytes)`: decode `bytes` as UTF-8, replacing each invalid sequence with U+FFFD the way
  `String::from_utf8_lossy` does, then escape the text. Borrow when the bytes are valid UTF-8 with nothing
  to escape. When decoding had to allocate but there's nothing to escape, return the decoded `String`
  itself: don't copy it again.
