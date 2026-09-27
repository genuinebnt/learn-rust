use std::borrow::Cow;
use std::ops::Range;

#[derive(Debug, Clone, PartialEq)]
pub enum Token<'a> {
    Ident(&'a str),
    Int(&'a str),
    /// The contents without the quotes, escapes resolved.
    Str(Cow<'a, str>),
    Op(&'a str),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LexError {
    /// The input ended inside a string; `at` is the opening quote.
    UnterminatedString { at: usize },
    /// A backslash followed by anything but `\`, `"`, `n` or `t`; `at` is the backslash.
    BadEscape { at: usize },
    /// A character that starts no token.
    Unexpected { at: usize, ch: char },
}

pub struct Lexer<'a> {
    src: &'a str,
    pos: usize,
    // add fields if you need them
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a str) -> Self {
        Lexer { src, pos: 0 }
    }
}

impl<'a> Iterator for Lexer<'a> {
    type Item = Result<(Token<'a>, Range<usize>), LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        todo!()
    }
}
