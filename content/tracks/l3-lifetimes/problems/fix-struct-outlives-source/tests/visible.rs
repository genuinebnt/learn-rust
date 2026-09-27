use solution::*;

#[test]
fn two_docs() {
    check!(r#"["  hello\nworld", "x"]"#, first_lines(&["  hello\nworld".to_string(), "x".to_string()]), vec!["hello".to_string(), "x".to_string()]);
}

#[test]
fn blank_doc() {
    check!(r#"["\n"]"#, first_lines(&["\n".to_string()]), vec![String::new()]);
}

#[test]
fn none() {
    check!(r#"[]"#, first_lines(&[]).len(), 0);
}

#[test]
fn trailing_spaces() {
    check!(r#"["hi  "]"#, first_lines(&["hi  ".to_string()]), vec!["hi".to_string()]);
}

#[test]
fn leading_blank_lines() {
    check!(r#"["\n\n  a\nb"]"#, first_lines(&["\n\n  a\nb".to_string()]), vec!["a".to_string()]);
}
