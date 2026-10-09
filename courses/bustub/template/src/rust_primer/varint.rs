//! Variable-length integers: small numbers take few bytes, as in protobuf, SQLite and most log formats.

/// Why a byte string is not one varint.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum VarintError {
    /// The bytes end while the number is still going on.
    Truncated,
    /// The number does not fit in a `u64`.
    Overflow,
    /// The number is right but was written with more bytes than it needs.
    NonMinimal,
}

/// Appends the encoding of `value` to `out`: 7 bits per byte, the lowest group first, and the high bit of a byte says another byte follows.
pub fn encode_varint(value: u64, out: &mut Vec<u8>) {
    todo!("r-c1: the varint format, as described on the challenge page")
}

/// Reads one varint from the start of `bytes`: the number and how many bytes it took. Bytes after it are not looked at.
pub fn decode_varint(bytes: &[u8]) -> Result<(u64, usize), VarintError> {
    todo!("r-c1: read one varint, or say exactly why the bytes are not one")
}
