pub struct Cursor<'a> {
    src: &'a str,
    pos: usize,
}

impl<'a> Cursor<'a> {
    pub fn new(src: &'a str) -> Self {
        Cursor { src, pos: 0 }
    }

    fn skip_ws(&self) -> usize {
        let rest = &self.src[self.pos..];
        self.pos + (rest.len() - rest.trim_start().len())
    }

    pub fn number(&mut self) -> Option<u64> {
        let start = self.skip_ws();
        let rest = &self.src[start..];
        let len = rest.bytes().take_while(u8::is_ascii_digit).count();
        if len == 0 {
            return None;
        }
        let n = rest.bytes().take(len).fold(0u64, |n, d| n.wrapping_mul(10).wrapping_add(u64::from(d - b'0')));
        self.pos = start + len;
        Some(n)
    }

    pub fn ident(&mut self) -> Option<&'a str> {
        let src = self.src;
        let start = self.skip_ws();
        let rest = &src[start..];
        let b = rest.as_bytes();
        if !b.first().is_some_and(|c| c.is_ascii_alphabetic() || *c == b'_') {
            return None;
        }
        let len = b.iter().take_while(|c| c.is_ascii_alphanumeric() || **c == b'_').count();
        self.pos = start + len;
        Some(&rest[..len])
    }

    pub fn rest(&self) -> &'a str {
        let src = self.src;
        &src[self.pos..]
    }
}
