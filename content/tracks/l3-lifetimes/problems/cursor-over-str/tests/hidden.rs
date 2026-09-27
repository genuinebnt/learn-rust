use solution::*;

#[test]
fn overflow() {
    check!(r#""99999999999999999999""#, Cursor::new("99999999999999999999").number(), None);
}

#[test]
fn u64_max() {
    check!(r#""18446744073709551615""#, Cursor::new("18446744073709551615").number(), Some(u64::MAX));
}

#[test]
fn one_past_max_keeps_position() {
    let mut c = Cursor::new(" 18446744073709551616");
    check!(r#"" 18446744073709551616": number, rest"#, (c.number(), c.rest()), (None, " 18446744073709551616"));
}

#[test]
fn leading_zeros() {
    check!(r#""007""#, Cursor::new("007").number(), Some(7));
}

#[test]
fn number_then_ident_adjacent() {
    let mut c = Cursor::new("12ab");
    check!(r#""12ab": number, ident, rest"#, (c.number(), c.ident(), c.rest()), (Some(12), Some("ab"), ""));
}

#[test]
fn ident_stops_at_punct() {
    let mut c = Cursor::new("a_1-b");
    check!(r#""a_1-b": ident, rest"#, (c.ident(), c.rest()), (Some("a_1"), "-b"));
}

#[test]
fn non_ascii_ident_start() {
    let mut c = Cursor::new("éa");
    check!(r#""éa": ident, rest"#, (c.ident(), c.rest()), (None, "éa"));
}

#[test]
fn tabs_and_newlines() {
    let mut c = Cursor::new("\t\n x \n 5");
    check!(r#""\t\n x \n 5": ident, number, rest"#, (c.ident(), c.number(), c.rest()), (Some("x"), Some(5), ""));
}

#[test]
fn minus_is_not_a_digit() {
    let mut c = Cursor::new("-5");
    check!(r#""-5": number, rest"#, (c.number(), c.rest()), (None, "-5"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(306);
    for _ in 0..300 {
        // Build a source from known tokens, then read it back with the matching method.
        let count = rng.below(5);
        let mut src = String::new();
        let mut tokens: Vec<(bool, String)> = Vec::new();
        for _ in 0..count {
            let spaces = rng.below(3);
            src.push_str(&" ".repeat(spaces));
            if rng.bool() {
                let len = rng.below(3);
                let tok = rng.string(1, "ab_") + &rng.string(len, "ab_1");
                src.push_str(&tok);
                tokens.push((true, tok));
            } else {
                let len = 1 + rng.below(4);
                let tok = rng.string(len, "0123456789");
                src.push_str(&tok);
                tokens.push((false, tok));
            }
            src.push(' ');
        }
        let mut c = Cursor::new(&src);
        for (is_ident, tok) in &tokens {
            if *is_ident {
                check!(format!("src = {src:?}, number() where an ident is"), c.number(), None);
                check!(format!("src = {src:?}"), c.ident(), Some(tok.as_str()));
            } else {
                check!(format!("src = {src:?}, ident() where a number is"), c.ident(), None);
                check!(format!("src = {src:?}"), c.number(), Some(tok.parse::<u64>().unwrap()));
            }
        }
        check!(format!("src = {src:?}: rest at the end"), c.rest().trim(), "");
    }
}

#[test]
fn digit_first() {
    let mut c = Cursor::new("9abc");
    check!(r#""9abc": ident, then number, then ident"#, (c.ident(), c.number(), c.ident()), (None, Some(9), Some("abc")));
}

#[test]
fn underscore() {
    check!(r#""_x1 rest""#, Cursor::new("_x1 rest").ident(), Some("_x1"));
}

#[test]
fn unicode_after() {
    let mut c = Cursor::new("n é");
    check!(r#""n é": ident, rest"#, (c.ident(), c.rest()), (Some("n"), " é"));
}
