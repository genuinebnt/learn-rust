use solution::*;

#[test]
fn unicode_punct() {
    check!(r#""a→b""#, Tokenizer::new("a→b").collect::<Vec<_>>(), vec![Token::Ident("a"), Token::Punct('→'), Token::Ident("b")]);
}

#[test]
fn blank() {
    check!(r#""   ""#, Tokenizer::new("   ").count(), 0);
}

#[test]
fn tie_first() {
    check!(r#""ab cd""#, longest_ident(Tokenizer::new("ab cd")), Some("ab"));
}

#[test]
fn numbers_are_not_idents() {
    check!(r#""12345 ab""#, longest_ident(Tokenizer::new("12345 ab")), Some("ab"));
}

#[test]
fn from_a_vec() {
    check!(r#"a Vec<Token> built by hand"#, longest_ident(vec![Token::Punct('x'), Token::Ident("q")]), Some("q"));
}
