use solution::*;

#[test]
fn three_words() {
    check!(r#"text = "the quick fox""#, summarize("the quick fox"), (3, "quick".to_string()));
}

#[test]
fn empty() {
    check!(r#"text = """#, summarize(""), (0, String::new()));
}

#[test]
fn single_word() {
    check!(r#"text = "rust""#, summarize("rust"), (1, "rust".to_string()));
}

#[test]
fn tie_first_wins() {
    check!(r#"text = "cat dog""#, summarize("cat dog"), (2, "cat".to_string()));
}

#[test]
fn extra_spaces() {
    check!(r#"text = "  a  bb ""#, summarize("  a  bb "), (2, "bb".to_string()));
}
