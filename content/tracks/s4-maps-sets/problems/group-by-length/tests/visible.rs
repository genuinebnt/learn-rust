use solution::*;

#[test]
fn mixed() {
    check!(r#"["hi", "yes", "no", "ok"]"#, group_by_len(&["hi", "yes", "no", "ok"]), std::collections::HashMap::from([(2, vec!["hi", "no", "ok"]), (3, vec!["yes"])]));
}

#[test]
fn empty() {
    check!(r#"[]"#, group_by_len(&[]), std::collections::HashMap::new());
}
