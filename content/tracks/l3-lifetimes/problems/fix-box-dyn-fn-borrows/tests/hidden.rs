use solution::*;

#[test]
fn many_calls() {
    let allowed = vec!["a"];
    let f = make_filter(&allowed);
    let words = ["a", "b", "a"];
    check!(r#"allowed ["a"]"#, words.iter().filter(|w| f(w)).count(), 2);
}

#[test]
fn empty_word_allowed() {
    let allowed = [""];
    let f = make_filter(&allowed);
    check!(r#"allowed [""]: """#, (f(""), f("x")), (true, false));
}

#[test]
fn empty_word_not_allowed() {
    check!(r#"allowed ["a"]: """#, make_filter(&["a"])(""), false);
}

#[test]
fn unicode() {
    let allowed = ["café"];
    let f = make_filter(&allowed);
    check!(r#"allowed ["café"]: "café", "cafe""#, (f("café"), f("cafe")), (true, false));
}

#[test]
fn duplicates() {
    check!(r#"allowed ["x", "x"]"#, make_filter(&["x", "x"])("x"), true);
}

#[test]
fn word_from_a_short_string() {
    let allowed = ["tmp"];
    let f = make_filter(&allowed);
    let ok = { let w = String::from("tmp"); f(&w) };
    check!(r#"the word is a String dropped right after the call"#, ok, true);
}

#[test]
fn whitespace_matters() {
    check!(r#"allowed ["a"]: " a""#, make_filter(&["a"])(" a"), false);
}

#[test]
fn many_allowed() {
    let owned: Vec<String> = (0..1000).map(|i| format!("n{i}")).collect();
    let allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
    let f = make_filter(&allowed);
    check!(r#"allowed n0..n999, ask n999 and n1000"#, (f("n999"), f("n1000")), (true, false));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(320);
    for _ in 0..300 {
        let n = rng.below(4);
        let owned: Vec<String> = (0..n).map(|_| { let len = rng.below(3); rng.string(len, "ab") }).collect();
        let allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let len = rng.below(3);
        let word = rng.string(len, "ab");
        let f = make_filter(&allowed);
        check!(format!("allowed = {allowed:?}, word = {word:?}"), f(&word), allowed.contains(&word.as_str()));
    }
}
