pub struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl<'a> Reader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Reader { data, pos: 0 }
    }

    /// The next `n` bytes, or None (reading nothing) if fewer remain.
    pub fn take(&mut self, n: usize) -> Option<&'a [u8]> {
        let chunk = self.data.get(self.pos..self.pos + n)?;
        self.pos += n;
        Some(chunk)
    }

    /// The next byte, without reading it.
    pub fn peek(&self) -> Option<u8> {
        self.data.get(self.pos).copied()
    }

    /// A big-endian `u16`, or None (reading nothing) if fewer than 2 bytes remain.
    pub fn u16(&mut self) -> Option<u16> {
        let b = self.take(2)?;
        Some(u16::from_be_bytes([b[0], b[1]]))
    }

    pub fn remaining(&self) -> usize {
        self.data.len() - self.pos
    }
}

/// Reads records, each a `u16` length then that many bytes, until the reader is empty. None if a record is
/// cut short (the reader is then left just after the last whole record).
pub fn records<'a>(r: &mut Reader<'a>) -> Option<Vec<&'a [u8]>> {
    let mut out = Vec::new();
    while r.remaining() > 0 {
        let start = r.pos;
        let Some(len) = r.u16() else {
            r.pos = start;
            return None;
        };
        let Some(body) = r.take(usize::from(len)) else {
            return None;
        };
        out.push(body);
    }
    Some(out)
}
