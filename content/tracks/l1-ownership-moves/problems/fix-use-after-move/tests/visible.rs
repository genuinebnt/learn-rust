use solution::*;

#[test]
fn three_words() {
    check!(r#"text = "the quick fox""#, summarize("the quick fox"), (3, "quick".to_string()));
}

#[test]
fn empty() {
    check!(r#"text = """#, summarize(""), (0, String::new()));
}
