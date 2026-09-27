`Cursor` walks a borrowed `&'a str`. Each method first skips whitespace, then reads its token.
On failure it returns `None` and leaves the cursor where it was.

- `number` reads ASCII digits as a `u64`; `None` if there are none or they overflow.
- `ident` reads an identifier: ASCII letters, digits and `_`, not starting with a digit.
- `rest` returns what hasn't been read.

Tokens must stay usable after the cursor is gone.
