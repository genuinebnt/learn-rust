/// Parses `tag, len, value` records (`len` is one byte; the value is `len` bytes). A leading "TLV" magic is
/// skipped. `None` if a record is cut short. Values borrow from `data`.
pub fn parse_tlv(data: &[u8]) -> Option<Vec<(u8, &[u8])>> {
    todo!()
}

/// The records encoded as `tag, len, value`, in one allocation of exactly the right size. `None` if a
/// value is longer than 255 bytes.
pub fn encode_tlv(records: &[(u8, &[u8])]) -> Option<Vec<u8>> {
    todo!()
}

/// The records' values, joined with `sep` between them.
pub fn join_values(records: &[(u8, &[u8])], sep: u8) -> Vec<u8> {
    todo!()
}
