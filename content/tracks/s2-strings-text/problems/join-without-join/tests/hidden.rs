use solution::*;

#[test]
fn none() {
    check!(r#"words = [], sep = "-""#, join_words(&[], "-"), String::new());
}

#[test]
fn empty_sep() {
    check!(r#"words = ["a", "b"], sep = """#, join_words(&["a", "b"], ""), "ab".to_string());
}

#[test]
fn unicode_sep() {
    check!(r#"words = ["x", "y"], sep = " → ""#, join_words(&["x", "y"], " → "), "x → y".to_string());
}
