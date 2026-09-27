use solution::*;

#[test]
fn mixed() {
    check!(r#""let x1 = 42+y;""#, Tokenizer::new("let x1 = 42+y;").collect::<Vec<_>>(), vec![Token::Ident("let"), Token::Ident("x1"), Token::Punct('='), Token::Number("42"), Token::Punct('+'), Token::Ident("y"), Token::Punct(';')]);
}

#[test]
fn longest_outlives_tokenizer() {
    let src = String::from("a bb ccc dd");
    let best;
    {
        let t = Tokenizer::new(&src);
        best = longest_ident(t);
    }
    check!(r#""a bb ccc dd""#, best, Some("ccc"));
}
