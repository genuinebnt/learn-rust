Three formatters. Use format specs for all the padding; no manual space counting.

- `table(rows, prec)`: one line per row, each ending in `\n`. The name is left-aligned and padded to the
  longest name (in characters), then `" | "`, then the value with `prec` decimals, right-aligned to the
  widest formatted value.
- `register(value)`: `0x` and 8 lowercase hex digits, `" = "`, then the 32 bits, most significant byte
  first, as four groups of 8 joined by `_`.
- `hexdump_line(offset, bytes)` (at most 16 bytes), as `hexdump -C` prints it: the offset as 8 hex
  digits, two spaces, then each byte as 2 lowercase hex digits and a space, with one extra space after
  the 8th byte. That hex part is padded with spaces to 49 columns. Then a space, `|`, each byte as its
  ASCII character if it's printable (graphic or a space) and `.` otherwise, and `|`.
