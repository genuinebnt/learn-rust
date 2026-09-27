use solution::*;

#[test]
fn case_folds() {
    check!(r#"["Alice", "alice", "Bob"]"#, distinct(&["Alice", "alice", "Bob"]), 2);
}

#[test]
fn already_distinct() {
    check!(r#"["a", "b"]"#, distinct(&["a", "b"]), 2);
}
