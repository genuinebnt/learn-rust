use solution::*;

#[test]
fn tie_keeps_first() {
    check!(r#"text = "ab cd""#, summarize("ab cd"), (2, "ab".to_string()));
}
