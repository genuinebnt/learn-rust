use solution::*;

#[test]
fn many_calls() {
    let allowed = vec!["a"];
    let f = make_filter(&allowed);
    let words = ["a", "b", "a"];
    check!(r#"allowed ["a"]"#, words.iter().filter(|w| f(w)).count(), 2);
}
