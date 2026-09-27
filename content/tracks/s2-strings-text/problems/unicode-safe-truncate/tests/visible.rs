use solution::*;

#[test]
fn ascii() {
    check!(r#""hello world", 8"#, truncate("hello world", 8), "hello…".to_string());
}

#[test]
fn fits() {
    check!(r#""short", 10"#, truncate("short", 10), "short".to_string());
}
