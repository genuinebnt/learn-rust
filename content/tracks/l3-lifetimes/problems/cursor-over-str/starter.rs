pub struct Cursor<'a> {
    src: &'a str,
    pos: usize,
}

impl<'a> Cursor<'a> {
    pub fn new(src: &'a str) -> Self {
        Cursor { src, pos: 0 }
    }

    pub fn number(&mut self) -> Option<u64> {
        todo!()
    }

    pub fn ident(&mut self) -> Option<&'a str> {
        todo!()
    }

    pub fn rest(&self) -> &'a str {
        todo!()
    }
}
