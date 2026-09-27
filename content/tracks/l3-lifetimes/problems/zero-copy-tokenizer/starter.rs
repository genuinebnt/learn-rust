#[derive(Debug, PartialEq, Clone, Copy)]
pub enum Token<'a> {
    Ident(&'a str),
    Number(&'a str),
    Punct(char),
}

pub struct Tokenizer<'a> {
    rest: &'a str,
}

impl<'a> Tokenizer<'a> {
    pub fn new(src: &'a str) -> Self {
        Tokenizer { rest: src }
    }
}

impl<'a> Iterator for Tokenizer<'a> {
    type Item = Token<'a>;

    fn next(&mut self) -> Option<Token<'a>> {
        todo!()
    }
}

pub fn longest_ident<'a, I: IntoIterator<Item = Token<'a>>>(tokens: I) -> Option<&'a str> {
    todo!()
}
