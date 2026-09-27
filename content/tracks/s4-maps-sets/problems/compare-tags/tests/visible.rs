use solution::*;

#[test]
fn overlap() {
    check!(r#"a = [rust, go, sql], b = [sql, rust, c]"#, compare_tags(&["rust", "go", "sql"], &["sql", "rust", "c"]), (vec!["rust".to_string(), "sql".to_string()], vec!["go".to_string()], vec!["c".to_string()]));
}

#[test]
fn disjoint() {
    check!(r#"a = [a], b = [b]"#, compare_tags(&["a"], &["b"]), (vec![], vec!["a".to_string()], vec!["b".to_string()]));
}
