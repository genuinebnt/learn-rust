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
fn ampersand() {
    check!(r#""a&b""#, escape_html("a&b").into_owned(), "a&amp;b".to_string());
}

#[test]
fn already_escaped() {
    check!(r#""&lt;""#, escape_html("&lt;").into_owned(), "&amp;lt;".to_string());
}

#[test]
fn quotes_and_gt() {
    check!(r#""\"x\" > y""#, escape_html("\"x\" > y").into_owned(), "&quot;x&quot; &gt; y".to_string());
}
