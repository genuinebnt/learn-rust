use solution::*;

#[test]
fn duplicates() {
    check!(r#"a = [x, x], b = [x]"#, compare_tags(&["x", "x"], &["x"]), (vec!["x".to_string()], vec![], vec![]));
}
