Implement CRC-8 for any polynomial `POLY` (initial value 0, bits processed most significant first, no final
XOR). For each input byte: `crc ^= byte`, then 8 times shift `crc` left by one, XORing in `POLY` whenever the
bit shifted out was 1.

`make_table(poly)` returns `table[b]` = the CRC of the single byte `b`. `Crc8::<POLY>::TABLE` stores it,
computed by the compiler, and `checksum` does one table lookup per byte:
`crc = TABLE[(crc ^ byte) as usize]`. Both must be usable in `const` items; the tests call them there.
