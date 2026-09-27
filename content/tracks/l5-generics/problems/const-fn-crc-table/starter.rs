/// CRC-8 with polynomial `POLY`: initial value 0, no reflection, no final XOR.
pub struct Crc8<const POLY: u8>;

/// `table[b]` is the CRC of the single byte `b`.
pub const fn make_table(poly: u8) -> [u8; 256] {
    // TODO: build the table. (A placeholder, so the crate compiles.)
    [0; 256]
}

impl<const POLY: u8> Crc8<POLY> {
    /// Built at compile time, once per polynomial.
    pub const TABLE: [u8; 256] = make_table(POLY);

    pub const fn checksum(data: &[u8]) -> u8 {
        // TODO: one table lookup per byte. (A placeholder, so the crate compiles.)
        0
    }
}
