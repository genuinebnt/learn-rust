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
        let s = self.rest.trim_start();
        let b = *s.as_bytes().first()?;
        let is_ident = |b: u8| b.is_ascii_alphanumeric() || b == b'_';
        let len = if b.is_ascii_alphabetic() || b == b'_' {
            s.bytes().take_while(|&b| is_ident(b)).count()
        } else if b.is_ascii_digit() {
            s.bytes().take_while(u8::is_ascii_digit).count()
        } else {
            s.chars().next().map_or(1, char::len_utf8)
        };
        let (text, rest) = s.split_at(len);
        self.rest = rest;
        Some(if b.is_ascii_alphabetic() || b == b'_' {
            Token::Ident(text)
        } else if b.is_ascii_digit() {
            Token::Number(text)
        } else {
            Token::Punct(b as char)
        })
    }
}

pub fn longest_ident<'a, I: IntoIterator<Item = Token<'a>>>(tokens: I) -> Option<&'a str> {
    tokens
        .into_iter()
        .filter_map(|t| match t {
            Token::Ident(s) => Some(s),
            _ => None,
        })
        .reduce(|best, s| if s.len() > best.len() { s } else { best })
}
