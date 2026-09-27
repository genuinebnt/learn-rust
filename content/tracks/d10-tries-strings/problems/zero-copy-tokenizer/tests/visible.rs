use solution::*;

use std::borrow::Cow;

fn kinds(src: &str) -> Result<Vec<Token<'_>>, LexError> {
    Lexer::new(src).map(|r| r.map(|(t, _)| t)).collect()
}

#[test]
fn let_statement() {
    check!(r#"src = "let x1 = 42;""#, kinds("let x1 = 42;"), Ok(vec![Token::Ident("let"), Token::Ident("x1"), Token::Op("="), Token::Int("42"), Token::Op(";")]));
}

#[test]
fn spans_are_byte_ranges() {
    check!(r#"src = "a == \"hé\"" (é is two bytes)"#, Lexer::new("a == \"hé\"").map(|r| r.unwrap()).collect::<Vec<_>>(), vec![(Token::Ident("a"), 0..1), (Token::Op("=="), 2..4), (Token::Str(Cow::Borrowed("hé")), 5..10)]);
}

#[test]
fn longest_operator_wins() {
    check!(r#"src = "a->b<=c""#, kinds("a->b<=c"), Ok(vec![Token::Ident("a"), Token::Op("->"), Token::Ident("b"), Token::Op("<="), Token::Ident("c")]));
}

#[test]
fn plain_string_is_borrowed() {
    check!(r#"src = "\"hi\"" (no escape: the token borrows src)"#, matches!(&kinds("\"hi\"").unwrap()[0], Token::Str(Cow::Borrowed("hi"))), true);
}

#[test]
fn escapes_make_an_owned_string() {
    let src = r#""a\"b\n""#;
    check!(r##"src = r#""a\"b\n""# (two escapes)"##, match kinds(src).unwrap().remove(0) {
        Token::Str(Cow::Owned(s)) => Some(s),
        _ => None,
    }, Some("a\"b\n".to_string()));
}

#[test]
fn comments_and_whitespace() {
    check!(r#"src = "x // note\n\t y""#, kinds("x // note\n\t y"), Ok(vec![Token::Ident("x"), Token::Ident("y")]));
}

#[test]
fn error_ends_the_stream() {
    let mut lx = Lexer::new("a @ b");
    check!(r#"src = "a @ b"; next() three times"#, (lx.next(), lx.next(), lx.next()), (Some(Ok((Token::Ident("a"), 0..1))), Some(Err(LexError::Unexpected { at: 2, ch: '@' })), None));
}

#[test]
fn unterminated_string() {
    check!(r#"src = "x = \"abc""#, kinds("x = \"abc"), Err(LexError::UnterminatedString { at: 4 }));
}

#[test]
fn empty() {
    check!(r#"src = """#, kinds(""), Ok(vec![]));
}
