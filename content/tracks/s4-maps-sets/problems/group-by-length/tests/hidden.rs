use solution::*;

#[test]
fn empty_string() {
    check!(r#"["", "a", ""]"#, group_by_len(&["", "a", ""]), std::collections::HashMap::from([(0, vec!["", ""]), (1, vec!["a"])]));
}
