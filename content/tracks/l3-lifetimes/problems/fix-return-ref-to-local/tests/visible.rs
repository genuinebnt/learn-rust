use solution::*;

#[test]
fn two_words() {
    check!(r#""Hello World""#, slug("Hello World"), "hello-world".to_string());
}

#[test]
fn extra_spaces() {
    check!(r#""  Rust  Is Fun ""#, slug("  Rust  Is Fun "), "rust-is-fun".to_string());
}
