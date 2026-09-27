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

#[test]
fn tabs_and_newlines() {
    let mut p = Parser::<Whitespace>::new("\ta\n b\r\n");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#""\ta\n b\r\n" with Whitespace"#, tokens, vec!["a", "b"]);
}

#[test]
fn unicode() {
    let mut p = Parser::<Whitespace>::new("héllo wörld");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#""héllo wörld" with Whitespace"#, tokens, vec!["héllo", "wörld"]);
}

#[test]
fn stays_none_after_end() {
    let mut p = Parser::<Whitespace>::new("x");
    check!(r#""x": advance three times, then current"#, (p.advance(), p.advance(), p.advance(), p.current()), (Some("x"), None, None, None));
}

#[test]
fn only_commas() {
    check!(r#"" , ,," with Comma"#, Parser::<Comma>::new(" , ,,").advance(), None);
}

#[test]
fn comma_newline_is_whitespace() {
    let mut p = Parser::<Comma>::new("a,\n b");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#""a,\n b" with Comma"#, tokens, vec!["a", "b"]);
}

#[test]
fn whitespace_keeps_commas() {
    let mut p = Parser::<Whitespace>::new("a,b c");
    let tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
    check!(r#""a,b c" with Whitespace"#, tokens, vec!["a,b", "c"]);
}

#[test]
fn next_token_direct() {
    check!(r#"Comma::next_token(" a , b")"#, Comma::next_token(" a , b"), Some(("a", ", b")));
}

#[test]
fn zero_copy() {
    let source = String::from("  hi");
    let tok = Parser::<Whitespace>::new(&source).advance().unwrap();
    check!(r#"token points into the source"#, std::ptr::eq(tok.as_ptr(), source[2..].as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(318);
    for _ in 0..300 {
        let n = rng.below(12);
        let src = rng.string(n, "ab ,\t");
        let want_ws: Vec<&str> = src.split(|c: char| c == ' ' || c == '\t').filter(|t| !t.is_empty()).collect();
        let want_comma: Vec<&str> = src.split(',').map(|t| t.trim()).filter(|t| !t.is_empty()).collect();
        let mut p = Parser::<Whitespace>::new(&src);
        let got_ws: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
        let mut q = Parser::<Comma>::new(&src);
        let got_comma: Vec<&str> = std::iter::from_fn(|| q.advance()).collect();
        check!(format!("src = {src:?}"), (got_ws, got_comma), (want_ws, want_comma));
    }
}
