use solution::*;

#[test]
fn define_or_echo_example() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define_or_echo rust, go"#, (g.define_or_echo("rust"), g.define_or_echo("go")), ("a language", "go"));
}

#[test]
fn pick_outlives_the_glossary() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    let (a, b) = (String::from("ok"), String::from("borrow"));
    let w = g.pick(&a, &b);
    drop(g);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; pick(ok, borrow), then drop the glossary"#, w, "borrow");
}

#[test]
fn define_first_outlives_the_text() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    let d = define_first(&g, &String::from("rust is fun"));
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define_first of a temporary "rust is fun""#, d, Some("a language"));
}

#[test]
fn pick_tie_goes_to_a() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; pick(zzz, yyy): neither defined"#, g.pick("zzz", "yyy"), "zzz");
}

#[test]
fn echo_of_a_temporary() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    let s = g.define_or_echo(&String::from("x")).to_string();
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define_or_echo of a word that's dropped after the call"#, s, "x".to_string());
}

#[test]
fn first_word_example() {
    check!(r#"first_word("hello world"), first_word("")"#, (first_word("hello world"), first_word("")), ("hello", ""));
}
