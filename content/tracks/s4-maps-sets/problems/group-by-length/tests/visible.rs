use solution::*;

#[test]
fn mixed() {
    check!(r#"["hi", "yes", "no", "ok"]"#, group_by_len(&["hi", "yes", "no", "ok"]), std::collections::HashMap::from([(2, vec!["hi", "no", "ok"]), (3, vec!["yes"])]));
}

#[test]
fn empty() {
    check!(r#"[]"#, group_by_len(&[]), std::collections::HashMap::new());
}

#[test]
fn empty_string() {
    check!(r#"["", "a", ""]"#, group_by_len(&["", "a", ""]), std::collections::HashMap::from([(0, vec!["", ""]), (1, vec!["a"])]));
}

#[test]
fn input_order_kept() {
    check!(r#"["bb", "aa", "cc"]"#, group_by_len(&["bb", "aa", "cc"]), std::collections::HashMap::from([(2, vec!["bb", "aa", "cc"])]));
}

#[test]
fn single() {
    check!(r#"["a"]"#, group_by_len(&["a"]), std::collections::HashMap::from([(1, vec!["a"])]));
}
