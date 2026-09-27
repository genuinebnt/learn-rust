use solution::*;

#[test]
fn escapes() {
    check!(r#""a<b""#, escape_html("a<b").into_owned(), "a&lt;b".to_string());
}

#[test]
fn borrows() {
    check!(r#""plain""#, matches!(escape_html("plain"), std::borrow::Cow::Borrowed("plain")), true);
}
