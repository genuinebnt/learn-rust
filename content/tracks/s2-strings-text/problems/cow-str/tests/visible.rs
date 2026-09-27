use solution::*;

#[test]
fn escapes() {
    check!(r#""a<b""#, escape_html("a<b").into_owned(), "a&lt;b".to_string());
}

#[test]
fn borrows() {
    check!(r#""plain""#, matches!(escape_html("plain"), std::borrow::Cow::Borrowed("plain")), true);
}

#[test]
fn already_escaped() {
    check!(r#""&lt;""#, escape_html("&lt;").into_owned(), "&amp;lt;".to_string());
}

#[test]
fn bytes_valid_and_plain_borrow() {
    check!(r#"b"plain""#, matches!(escape_bytes(b"plain"), std::borrow::Cow::Borrowed("plain")), true);
}

#[test]
fn bytes_invalid_replaced() {
    check!(r#"b"a\xffb""#, escape_bytes(b"a\xffb").into_owned(), "a\u{FFFD}b".to_string());
}
