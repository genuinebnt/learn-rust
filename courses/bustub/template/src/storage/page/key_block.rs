//! A block of sorted keys with the shared prefix of each key left out.

/// The keys must be sorted and at most 255 bytes each, and there are at most 255 of them.
pub fn encode_keys(keys: &[Vec<u8>]) -> Vec<u8> {
    todo!("2a-c4: the count, then (shared, rest length, rest) for each key")
}

/// The keys of a block, or `None` if the bytes are not exactly one well-formed block.
pub fn decode_keys(bytes: &[u8]) -> Option<Vec<Vec<u8>>> {
    todo!("2a-c4: rebuild each key from the previous key's prefix; refuse anything malformed")
}
