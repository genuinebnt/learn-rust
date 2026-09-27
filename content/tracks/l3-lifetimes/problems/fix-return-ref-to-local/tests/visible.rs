use solution::*;

#[test]
fn two_words() {
    check!(r#""Hello World""#, slug("Hello World"), "hello-world".to_string());
}

#[test]
fn extra_spaces() {
    check!(r#""  Rust  Is Fun ""#, slug("  Rust  Is Fun "), "rust-is-fun".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, slug(""), String::new());
}

#[test]
fn one_word() {
    check!(r#""Rust""#, slug("Rust"), "rust".to_string());
}

#[test]
fn tabs_and_newlines() {
    check!(r#""a\tB\nc""#, slug("a\tB\nc"), "a-b-c".to_string());
}
