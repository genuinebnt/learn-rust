- `natural_cmp(a, b)`: the order a file browser uses, so `"file9"` sorts before `"file10"`. Walk both
  strings together. Where both have a run of ASCII digits, compare the runs by numeric value (they can be
  any length). Otherwise compare one character at a time by code point; a string that runs out first is
  smaller. If everything compares equal, fall back to comparing `a` and `b` as plain strings, so
  `"x01"` < `"x1"` and only identical strings are `Equal`.
- `luhn_valid(s)`: the Luhn checksum used by card numbers. Spaces are ignored; any other character that
  isn't an ASCII digit makes it invalid, and so do fewer than two digits. From the rightmost digit, double
  every second digit, subtracting 9 from any result above 9; the number is valid if the sum is a multiple
  of 10.
