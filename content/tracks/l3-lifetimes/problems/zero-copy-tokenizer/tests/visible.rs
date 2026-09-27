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

#[test]
fn empty() {
    check!(r#""""#, Tokenizer::new("").count(), 0);
}

#[test]
fn number_then_ident() {
    check!(r#""12ab _x9""#, Tokenizer::new("12ab _x9").collect::<Vec<_>>(), vec![Token::Number("12"), Token::Ident("ab"), Token::Ident("_x9")]);
}

#[test]
fn no_idents() {
    check!(r#""1 + 2""#, longest_ident(Tokenizer::new("1 + 2")), None);
}
