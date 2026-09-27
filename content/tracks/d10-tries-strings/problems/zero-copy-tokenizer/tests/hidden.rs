use solution::*;

use std::borrow::Cow;

fn kinds(src: &str) -> Result<Vec<Token<'_>>, LexError> {
    Lexer::new(src).map(|r| r.map(|(t, _)| t)).collect()
}

#[test]
fn bad_escape() {
    let src = r#""a\q""#;
    check!(r##"src = r#""a\q""#"##, kinds(src), Err(LexError::BadEscape { at: 2 }));
}

#[test]
fn backslash_at_the_end() {
    let src = r#""ab\"#;
    check!(r##"src = r#""ab\"#"##, kinds(src), Err(LexError::UnterminatedString { at: 0 }));
}

#[test]
fn escaped_quote_then_end() {
    let src = r#""ab\""#;
    check!(r##"src = r#""ab\""# (the quote is escaped, so the string never closes)"##, kinds(src), Err(LexError::UnterminatedString { at: 0 }));
}

#[test]
fn unicode_outside_a_string() {
    check!(r#"src = "a é""#, kinds("a é"), Err(LexError::Unexpected { at: 2, ch: 'é' }));
}

#[test]
fn unicode_inside_a_string() {
    check!(r#"src = "\"🦀\"""#, Lexer::new("\"🦀\"").map(|r| r.unwrap()).collect::<Vec<_>>(), vec![(Token::Str(Cow::Borrowed("🦀")), 0..6)]);
}

#[test]
fn maximal_munch() {
    check!(r#"src = "a-->b === ::< &&& !==""#, kinds("a-->b === ::< &&& !=="), Ok(["a", "-", "->", "b", "==", "=", "::", "<", "&&", "&", "!=", "="].map(|s| if s == "a" || s == "b" { Token::Ident(s) } else { Token::Op(s) }).to_vec()));
}

#[test]
fn comment_at_the_end() {
    check!(r#"src = "x //end""#, kinds("x //end"), Ok(vec![Token::Ident("x")]));
}

#[test]
fn only_a_comment() {
    check!(r#"src = "// just a comment""#, kinds("// just a comment"), Ok(vec![]));
}

#[test]
fn slash_is_an_operator() {
    check!(r#"src = "a / b/ /c""#, kinds("a / b/ /c"), Ok(vec![Token::Ident("a"), Token::Op("/"), Token::Ident("b"), Token::Op("/"), Token::Op("/"), Token::Ident("c")]));
}

#[test]
fn comment_marker_inside_a_string() {
    check!(r#"src = "\"// not\" y""#, kinds("\"// not\" y"), Ok(vec![Token::Str(Cow::Borrowed("// not")), Token::Ident("y")]));
}

#[test]
fn numbers_then_idents() {
    check!(r#"src = "12ab 007""#, kinds("12ab 007"), Ok(vec![Token::Int("12"), Token::Ident("ab"), Token::Int("007")]));
}

#[test]
fn newline_inside_a_string() {
    check!(r#"src = "\"a\nb\"""#, kinds("\"a\nb\""), Ok(vec![Token::Str(Cow::Borrowed("a\nb"))]));
}

#[test]
fn unicode_whitespace() {
    check!(r#"src = "a\u{3000}b\u{a0}c""#, kinds("a\u{3000}b\u{a0}c"), Ok(vec![Token::Ident("a"), Token::Ident("b"), Token::Ident("c")]));
}

#[test]
fn fused_after_an_error() {
    let mut lx = Lexer::new("\"x");
    check!(r#"src = "\"x"; next() three times"#, (lx.next(), lx.next(), lx.next()), (Some(Err(LexError::UnterminatedString { at: 0 })), None, None));
}

#[test]
fn escape_after_unicode() {
    let src = r#""é\té""#;
    check!(r##"src = r#""é\té""#"##, Lexer::new(src).map(|r| r.unwrap()).collect::<Vec<_>>(), vec![(Token::Str(Cow::Owned("é\té".to_string())), 0..8)]);
}

#[test]
fn bad_escape_after_unicode() {
    let src = r#""é\é""#;
    check!(r##"src = r#""é\é""# (é is two bytes)"##, kinds(src), Err(LexError::BadEscape { at: 3 }));
}

#[test]
fn punctuation() {
    check!(r#"src = "(a,b)[0]{c};x.y%z*w""#, kinds("(a,b)[0]{c};x.y%z*w").unwrap().len(), 19);
}

#[test]
fn zero_copy() {
    let src = String::from("name \"text\"");
    let toks: Vec<Token> = Lexer::new(&src).map(|r| r.unwrap().0).collect();
    let ok = match (&toks[0], &toks[1]) {
        (Token::Ident(a), Token::Str(Cow::Borrowed(b))) => std::ptr::eq(a.as_ptr(), src.as_ptr()) && std::ptr::eq(b.as_ptr(), src[6..].as_ptr()),
        _ => false,
    };
    check!(r#"idents and plain strings point into src"#, ok, true);
}

#[test]
fn tokens_outlive_the_lexer() {
    let src = String::from("fn main");
    let first;
    {
        let mut lx = Lexer::new(&src);
        first = lx.next();
    }
    check!(r#"src = "fn main"; keep the first item after the lexer is dropped"#, first, Some(Ok((Token::Ident("fn"), 0..2))));
}

#[test]
fn random_programs() {
    // Pieces with a known token, joined by trivia so they can't merge; sometimes an error at the end.
    let pieces: [(&str, Token); 12] = [
        ("abc", Token::Ident("abc")),
        ("_x1", Token::Ident("_x1")),
        ("42", Token::Int("42")),
        ("==", Token::Op("==")),
        ("=", Token::Op("=")),
        ("->", Token::Op("->")),
        ("-", Token::Op("-")),
        ("::", Token::Op("::")),
        ("\"hi\"", Token::Str(Cow::Borrowed("hi"))),
        ("\"a\\nb\"", Token::Str(Cow::Owned("a\nb".to_string()))),
        ("\"é\"", Token::Str(Cow::Borrowed("é"))),
        ("\"\"", Token::Str(Cow::Borrowed(""))),
    ];
    let gaps = [" ", "\n", "\t ", " // c\n"];
    let mut rng = anneal_prelude::Rng::new(1025);
    for _ in 0..300 {
        let mut src = String::new();
        let mut want: Vec<Result<(Token, std::ops::Range<usize>), LexError>> = Vec::new();
        let mut owned = Vec::new();
        for _ in 0..rng.below(8) {
            let (text, tok) = rng.pick(&pieces).clone();
            let start = src.len();
            src.push_str(text);
            owned.push(matches!(tok, Token::Str(Cow::Owned(_))));
            want.push(Ok((tok, start..src.len())));
            let gap: &str = *rng.pick(&gaps);
    src.push_str(gap);
        }
        match rng.below(4) {
            0 => {
                want.push(Err(LexError::Unexpected { at: src.len(), ch: '@' }));
                src.push_str("@ x");
            }
            1 => {
                want.push(Err(LexError::UnterminatedString { at: src.len() }));
                src.push_str("\"open");
            }
            2 => {
                want.push(Err(LexError::BadEscape { at: src.len() + 2 }));
                src.push_str("\"b\\q\" x");
            }
            _ => {}
        }
        let got: Vec<_> = Lexer::new(&src).collect();
        let got_owned: Vec<bool> = got.iter().filter_map(|r| r.as_ref().ok()).map(|(t, _)| matches!(t, Token::Str(Cow::Owned(_)))).collect();
        check!(format!("src = {src:?}"), got, want.clone());
        check!(format!("src = {src:?}: which strings are owned"), got_owned, owned);
    }
}

#[test]
fn scale_million_bytes() {
    let line = "let x_1 = \"str\\n\" + 42; // c\n";
    let src = line.repeat(40_000);
    let (mut count, mut owned, mut last) = (0, 0, 0..0);
    for item in Lexer::new(&src) {
        let (tok, span) = item.unwrap();
        count += 1;
        owned += matches!(tok, Token::Str(Cow::Owned(_))) as usize;
        last = span;
    }
    let semi = src.len() - line.len() + line.find(';').unwrap();
    check!("src = 40000 lines of `let x_1 = \"str\\n\" + 42; // c`", (count, owned, last), (280_000, 40_000, semi..semi + 1));
}
