use solution::*;

#[test]
fn filters() {
    let owned = vec![String::from("red"), String::from("blue")];
    let allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
    let f = make_filter(&allowed);
    check!(r#"allowed ["red", "blue"] built from Strings"#, (f("red"), f("green")), (true, false));
}

#[test]
fn empty() {
    check!(r#"allowed []"#, make_filter(&[])("x"), false);
}

#[test]
fn many_calls() {
    let allowed = vec!["a"];
    let f = make_filter(&allowed);
    let words = ["a", "b", "a"];
    check!(r#"allowed ["a"]"#, words.iter().filter(|w| f(w)).count(), 2);
}

#[test]
fn exact_match_only() {
    let allowed = ["red"];
    let f = make_filter(&allowed);
    check!(r#"allowed ["red"]: "re", "reds""#, (f("re"), f("reds"), f("red")), (false, false, true));
}

#[test]
fn case_sensitive() {
    check!(r#"allowed ["Red"]: "red""#, make_filter(&["Red"])("red"), false);
}
