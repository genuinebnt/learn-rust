use std::marker::PhantomData;

pub trait Tokenize {
    /// Splits the next token off `input`, returning (token, remainder).
    fn next_token(input: &str) -> Option<(&str, &str)>;
}

pub struct Whitespace;

pub struct Comma;

impl Tokenize for Whitespace {
    fn next_token(input: &str) -> Option<(&str, &str)> {
        todo!()
    }
}

impl Tokenize for Comma {
    fn next_token(input: &str) -> Option<(&str, &str)> {
        todo!()
    }
}

pub struct Parser<'a, T> {
    // Replace this with the fields you need. The source text is owned by the caller.
    _todo: PhantomData<(&'a str, T)>,
}

impl<'a, T: Tokenize> Parser<'a, T> {
    pub fn new(source: &'a str) -> Self {
        todo!()
    }

    pub fn advance(&mut self) -> Option<&'a str> {
        todo!()
    }

    pub fn current(&self) -> Option<&'a str> {
        todo!()
    }
}
