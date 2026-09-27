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

/// Two-character operators come first, so the longest match wins.
const OPS: &[&str] = &[
    "==", "!=", "<=", ">=", "->", "=>", "&&", "||", "::", "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", ":", ";", ",", ".", "(", ")", "{", "}", "[", "]",
];

pub struct Lexer<'a> {
    src: &'a str,
    pos: usize,
    /// Set after the end or an error; the lexer is fused from then on.
    done: bool,
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a str) -> Self {
        Lexer { src, pos: 0, done: false }
    }

    /// Moves `pos` past whitespace and `//` comments.
    fn skip_trivia(&mut self) {
        loop {
            let rest = &self.src[self.pos..];
            let trimmed = rest.trim_start();
            self.pos += rest.len() - trimmed.len();
            if !trimmed.starts_with("//") {
                return;
            }
            self.pos += trimmed.find('\n').unwrap_or(trimmed.len());
        }
    }

    fn lex(&mut self) -> Option<Result<(Token<'a>, Range<usize>), LexError>> {
        self.skip_trivia();
        let src: &'a str = self.src;
        let start = self.pos;
        let rest = &src[start..];
        let c = rest.chars().next()?;
        let (token, len) = if c.is_ascii_alphabetic() || c == '_' {
            let len = rest.find(|c: char| !(c.is_ascii_alphanumeric() || c == '_')).unwrap_or(rest.len());
            (Token::Ident(&rest[..len]), len)
        } else if c.is_ascii_digit() {
            let len = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
            (Token::Int(&rest[..len]), len)
        } else if c == '"' {
            match string_literal(rest, start) {
                Ok(found) => found,
                Err(e) => return Some(Err(e)),
            }
        } else if let Some(op) = OPS.iter().find(|op| rest.starts_with(**op)) {
            (Token::Op(&rest[..op.len()]), op.len())
        } else {
            return Some(Err(LexError::Unexpected { at: start, ch: c }));
        };
        self.pos = start + len;
        Some(Ok((token, start..start + len)))
    }
}

/// Reads the string literal that `rest` starts with; `start` is its offset in the source.
/// Returns the token and its length in bytes, quotes included.
fn string_literal(rest: &str, start: usize) -> Result<(Token<'_>, usize), LexError> {
    let body = &rest[1..];
    // `None` until the first escape: up to then the contents are a plain slice of the source.
    let mut owned: Option<String> = None;
    let mut copied = 0; // bytes of `body` already copied into `owned`
    let mut chars = body.char_indices();
    while let Some((i, c)) = chars.next() {
        match c {
            '"' => {
                let text = match owned {
                    None => Cow::Borrowed(&body[..i]),
                    Some(mut s) => {
                        s.push_str(&body[copied..i]);
                        Cow::Owned(s)
                    }
                };
                return Ok((Token::Str(text), i + 2));
            }
            '\\' => {
                let Some((_, e)) = chars.next() else {
                    break; // the input ends right after the backslash
                };
                let resolved = match e {
                    '\\' => '\\',
                    '"' => '"',
                    'n' => '\n',
                    't' => '\t',
                    _ => return Err(LexError::BadEscape { at: start + 1 + i }),
                };
                let s = owned.get_or_insert_with(String::new);
                s.push_str(&body[copied..i]);
                s.push(resolved);
                copied = i + 1 + e.len_utf8();
            }
            _ => {}
        }
    }
    Err(LexError::UnterminatedString { at: start })
}

impl<'a> Iterator for Lexer<'a> {
    type Item = Result<(Token<'a>, Range<usize>), LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }
        let item = self.lex();
        self.done = item.is_none();
        item
    }
}

impl std::iter::FusedIterator for Lexer<'_> {}
