use solution::*;

#[test]
fn walks() {
    let source = String::from("parse me please");
    let mut p = Parser::<Whitespace>::new(&source);
    check!(r#""parse me please" with Whitespace"#, (p.advance(), p.advance(), p.current(), p.advance(), p.advance(), p.current()), (Some("parse"), Some("me"), Some("me"), Some("please"), None, None));
}

#[test]
fn tokens_outlive_parser() {
    let source = String::from("a b");
    let first;
    {
        let mut p = Parser::<Whitespace>::new(&source);
        first = p.advance();
    }
    check!(r#""a b"; drop the parser after one advance"#, first, Some("a"));
}
