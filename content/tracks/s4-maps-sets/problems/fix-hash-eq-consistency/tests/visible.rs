use solution::*;

#[test]
fn case_folds() {
    check!(r#"["Alice", "alice", "Bob"]"#, distinct(&["Alice", "alice", "Bob"]), 2);
}

#[test]
fn already_distinct() {
    check!(r#"["a", "b"]"#, distinct(&["a", "b"]), 2);
}

#[test]
fn many_cases() {
    check!(r#"["ADMIN", "admin", "Admin", "aDmIn"]"#, distinct(&["ADMIN", "admin", "Admin", "aDmIn"]), 1);
}

#[test]
fn empty() {
    check!(r#"[]"#, distinct(&[]), 0);
}

#[test]
fn prefix_is_different() {
    check!(r#"["ab", "A"]"#, distinct(&["ab", "A"]), 2);
}
