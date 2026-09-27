use solution::*;

#[test]
fn ascii() {
    check!(r#""hello world", 8"#, truncate("hello world", 8), "hello…".to_string());
}

#[test]
fn fits() {
    check!(r#""short", 10"#, truncate("short", 10), "short".to_string());
}

#[test]
fn only_room_for_ellipsis() {
    check!(r#""abcd", 3"#, truncate("abcd", 3), "…".to_string());
}

#[test]
fn cut_before_accent() {
    check!(r#""café au lait", 7"#, truncate("café au lait", 7), "caf…".to_string());
}

#[test]
fn empty_input() {
    check!(r#""", 0"#, truncate("", 0), String::new());
}
