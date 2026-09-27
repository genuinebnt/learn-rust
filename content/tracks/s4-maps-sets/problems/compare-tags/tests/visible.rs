use solution::*;

#[test]
fn overlap() {
    check!(r#"a = [rust, go, sql], b = [sql, rust, c]"#, compare_tags(&["rust", "go", "sql"], &["sql", "rust", "c"]), (vec!["rust".to_string(), "sql".to_string()], vec!["go".to_string()], vec!["c".to_string()]));
}

#[test]
fn disjoint() {
    check!(r#"a = [a], b = [b]"#, compare_tags(&["a"], &["b"]), (vec![], vec!["a".to_string()], vec!["b".to_string()]));
}

#[test]
fn duplicates() {
    check!(r#"a = [x, x], b = [x]"#, compare_tags(&["x", "x"], &["x"]), (vec!["x".to_string()], vec![], vec![]));
}

#[test]
fn both_empty() {
    check!(r#"a = [], b = []"#, compare_tags(&[], &[]), (Vec::<String>::new(), Vec::<String>::new(), Vec::<String>::new()));
}

#[test]
fn sorted_output() {
    check!(r#"a = [c, b, a], b = []"#, compare_tags(&["c", "b", "a"], &[]), (vec![], vec!["a".to_string(), "b".to_string(), "c".to_string()], vec![]));
}
