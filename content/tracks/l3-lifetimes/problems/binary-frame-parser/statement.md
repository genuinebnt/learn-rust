A frame is: magic `b"AN"` (2 bytes), a kind byte, a big-endian `u16` length, then that many payload
bytes.

- `parse_frame` returns the frame and the bytes after it, or `None` for a bad or truncated frame.
  The payload must borrow from `buf`.
- `parse_all` parses back-to-back frames until the buffer is empty; `None` if anything is left that
  isn't a whole frame.
