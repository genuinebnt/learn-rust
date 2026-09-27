use solution::*;

#[test]
fn two_docs() {
    check!(r#"["  hello\nworld", "x"]"#, first_lines(&["  hello\nworld".to_string(), "x".to_string()]), vec!["hello".to_string(), "x".to_string()]);
}

#[test]
fn blank_doc() {
    check!(r#"["\n"]"#, first_lines(&["\n".to_string()]), vec![String::new()]);
}
