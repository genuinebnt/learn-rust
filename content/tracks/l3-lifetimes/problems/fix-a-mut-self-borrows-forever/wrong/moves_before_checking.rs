pub struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
}

impl<'a> Reader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Reader { data, pos: 0 }
    }

    /// The next `n` bytes, or None if fewer remain.
    pub fn take(&mut self, n: usize) -> Option<&'a [u8]> {
        self.pos += n;
        let chunk = self.data.get(self.pos - n..self.pos)?;
        Some(chunk)
    }

    pub fn remaining(&self) -> usize {
        self.data.len().saturating_sub(self.pos)
    }
}
