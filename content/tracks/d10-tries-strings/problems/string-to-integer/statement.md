Read an `i32` from the start of `s`, the way C's `atoi` does:

1. skip leading spaces (only `' '`, no other whitespace);
2. read one optional sign, `'+'` or `'-'`;
3. read ASCII digits until the first non-digit or the end, skipping leading zeros;
4. clamp the result to `i32::MIN..=i32::MAX`.

If no digits were read, the answer is 0. Anything after the digits is ignored.
