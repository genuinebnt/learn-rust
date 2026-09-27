/// Parses `tag, len, value` records (`len` is one byte; the value is `len` bytes). A leading "TLV" magic is
/// skipped. `None` if a record is cut short. Values borrow from `data`.
pub fn parse_tlv(data: &[u8]) -> Option<Vec<(u8, &[u8])>> {
    let mut rest = data.strip_prefix(b"TLV").unwrap_or(data);
    let mut out = Vec::new();
    while let Some((&tag, after)) = rest.split_first() {
        let (&len, after) = after.split_first()?;
        let (value, after) = after.split_at_checked(usize::from(len))?;
        out.push((tag, value));
        rest = after;
    }
    Some(out)
}

/// The records encoded as `tag, len, value`, in one allocation of exactly the right size. `None` if a
/// value is longer than 255 bytes.
pub fn encode_tlv(records: &[(u8, &[u8])]) -> Option<Vec<u8>> {
    let mut out = Vec::new();
    for &(tag, value) in records {
        let len = u8::try_from(value.len()).ok()?;
        out.push(tag);
        out.push(len);
        out.extend_from_slice(value);
    }
    Some(out)
}

/// The records' values, joined with `sep` between them.
pub fn join_values(records: &[(u8, &[u8])], sep: u8) -> Vec<u8> {
    records.iter().map(|&(_, value)| value).collect::<Vec<_>>().join(&sep)
}
