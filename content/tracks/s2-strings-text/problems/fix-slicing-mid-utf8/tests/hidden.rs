use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀🦀🦀", 2"#, prefix("🦀🦀🦀", 2), "🦀🦀");
}

#[test]
fn zero() {
    check!(r#""abc", 0"#, prefix("abc", 0), "");
}

#[test]
fn shorter_in_chars_than_bytes() {
    check!(r#""日本", 3"#, prefix("日本", 3), "日本");
}
