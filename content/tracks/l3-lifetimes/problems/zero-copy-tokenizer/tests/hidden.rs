use solution::*;

#[test]
fn unicode_punct() {
    check!(r#""a→b""#, Tokenizer::new("a→b").collect::<Vec<_>>(), vec![Token::Ident("a"), Token::Punct('→'), Token::Ident("b")]);
}

#[test]
fn leading_zeros() {
    check!(r#""007""#, Tokenizer::new("007").collect::<Vec<_>>(), vec![Token::Number("007")]);
}

#[test]
fn punct_runs_split() {
    check!(r#""==>""#, Tokenizer::new("==>").collect::<Vec<_>>(), vec![Token::Punct('='), Token::Punct('='), Token::Punct('>')]);
}

#[test]
fn tabs_and_newlines() {
    check!(r#""a\n\tb""#, Tokenizer::new("a\n\tb").collect::<Vec<_>>(), vec![Token::Ident("a"), Token::Ident("b")]);
}

#[test]
fn non_ascii_letter_is_punct() {
    check!(r#""éa""#, Tokenizer::new("éa").collect::<Vec<_>>(), vec![Token::Punct('é'), Token::Ident("a")]);
}

#[test]
fn emoji() {
    check!(r#""x😀1""#, Tokenizer::new("x😀1").collect::<Vec<_>>(), vec![Token::Ident("x"), Token::Punct('😀'), Token::Number("1")]);
}

#[test]
fn zero_copy() {
    let src = String::from("1 + abc");
    let Some(Token::Ident(id)) = Tokenizer::new(&src).nth(2) else { panic!("no ident") };
    check!(r#"idents point into the source"#, std::ptr::eq(id.as_ptr(), src[4..].as_ptr()), true);
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

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(310);
    for _ in 0..300 {
        let n = rng.below(12);
        let src = rng.string(n, "a_1 +é");
        // Reference: classify one char at a time.
        let cs: Vec<(usize, char)> = src.char_indices().collect();
        let mut want: Vec<Token> = Vec::new();
        let mut i = 0;
        while i < cs.len() {
            let (at, c) = cs[i];
            let mut j = i + 1;
            if c == ' ' {
                i = j;
                continue;
            }
            if c == 'a' || c == '_' {
                while j < cs.len() && matches!(cs[j].1, 'a' | '_' | '1') {
                    j += 1;
                }
            } else if c == '1' {
                while j < cs.len() && cs[j].1 == '1' {
                    j += 1;
                }
            }
            let end = if j < cs.len() { cs[j].0 } else { src.len() };
            want.push(match c {
                'a' | '_' => Token::Ident(&src[at..end]),
                '1' => Token::Number(&src[at..end]),
                _ => Token::Punct(c),
            });
            i = j;
        }
        let longest = want.iter().filter_map(|t| if let Token::Ident(s) = t { Some(*s) } else { None }).fold(None, |best: Option<&str>, s| match best {
            Some(b) if b.len() >= s.len() => Some(b),
            _ => Some(s),
        });
        check!(format!("src = {src:?}"), Tokenizer::new(&src).collect::<Vec<_>>(), want.clone());
        check!(format!("src = {src:?}: longest_ident"), longest_ident(Tokenizer::new(&src)), longest);
    }
}
