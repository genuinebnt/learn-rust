use solution::*;

#[test]
fn single_char() {
    check!(r#"s = "a""#, { let mut o = String::new(); write_twice(&mut o, "a"); o }, "aa".to_string());
}

#[test]
fn with_newline() {
    check!(r#"s = "a\n""#, { let mut o = String::new(); write_twice(&mut o, "a\n"); o }, "a\na\n".to_string());
}

#[test]
fn long() {
    check!(r#"s = 1000 × "x""#, { let mut o = String::new(); let s = "x".repeat(1000); write_twice(&mut o, &s); o.len() }, 2000);
}

#[test]
fn emoji() {
    check!(r#"s = "🦀""#, { let mut o = String::new(); write_twice(&mut o, "🦀"); o }, "🦀🦀".to_string());
}

#[test]
fn existing_unicode() {
    check!(r#"out = "ü", s = "-""#, { let mut o = String::from("ü"); write_twice(&mut o, "-"); o }, "ü--".to_string());
}

#[test]
fn spaces() {
    check!(r#"out = "a", s = " ""#, { let mut o = String::from("a"); write_twice(&mut o, " "); o }, "a  ".to_string());
}

#[test]
fn both_empty() {
    check!(r#"out = "", s = """#, { let mut o = String::new(); write_twice(&mut o, ""); o }, String::new());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2011);
    for _ in 0..300 {
        let lo = rng.below(4);
        let start = rng.string(lo, "xyé");
        let ls = rng.below(4);
        let s = rng.string(ls, "ab é");
        let mut o = start.clone();
        write_twice(&mut o, &s);
        check!(format!("out = {start:?}, s = {s:?}"), o, format!("{start}{s}{s}"));
    }
}
