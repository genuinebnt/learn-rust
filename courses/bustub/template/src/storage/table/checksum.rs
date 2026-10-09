//! CRC-32 (IEEE) and sealed payloads.

#[derive(Debug, PartialEq, Eq)]
pub enum SealError {
    TooShort,
    Mismatch,
}

pub fn crc32(data: &[u8]) -> u32 {
    todo!("3b-c4: the table of 256 entries, then one table lookup per byte")
}

pub fn seal(payload: &[u8]) -> Vec<u8> {
    todo!("3b-c4: the payload, then its CRC in 4 little-endian bytes")
}

pub fn unseal(bytes: &[u8]) -> Result<&[u8], SealError> {
    todo!("3b-c4: check the stored CRC against the payload")
}
