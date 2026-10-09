//! A row of variable-length columns: end offsets, then the data.

pub fn encode(columns: &[Vec<u8>]) -> Vec<u8> {
    let mut out = vec![columns.len() as u8];
    let mut end = 0u16;
    for c in columns {
        end += c.len() as u16;
        out.extend_from_slice(&end.to_le_bytes());
    }
    for c in columns {
        out.extend_from_slice(c);
    }
    out
}

/// The bytes of column `i`.
pub fn column(bytes: &[u8], i: usize) -> Option<&[u8]> {
    let n = *bytes.first()? as usize;
    if i >= n {
        return None;
    }
    let offsets = bytes.get(1..1 + 2 * n)?;
    let data = bytes.get(1 + 2 * n..)?;
    let end_of = |k: usize| u16::from_le_bytes([offsets[2 * k], offsets[2 * k + 1]]) as usize;
    let start = end_of(i);
    data.get(start..end_of(i))
}
