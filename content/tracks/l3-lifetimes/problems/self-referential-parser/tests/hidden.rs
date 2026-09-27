use solution::*;

#[test]
fn comma() {
    let mut p = Parser::<Comma>::new("a, b,,c , ");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#""a, b,,c , " with Comma"#, tokens, vec!["a", "b", "c"]);
}

#[test]
fn before_first() {
    check!(r#"current() before advance"#, Parser::<Whitespace>::new("x").current(), None);
}

#[test]
fn empty() {
    check!(r#""   " with Whitespace"#, Parser::<Whitespace>::new("   ").advance(), None);
}

#[test]
fn comma_keeps_inner_spaces() {
    let mut p = Parser::<Comma>::new(" new york , la");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#"" new york , la" with Comma"#, tokens, vec!["new york", "la"]);
}
