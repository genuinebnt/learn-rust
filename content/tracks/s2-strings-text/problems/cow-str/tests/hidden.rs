use solution::*;

#[test]
fn all_five() {
    check!(r#""&<>\"'""#, escape_html("&<>\"'").into_owned(), "&amp;&lt;&gt;&quot;&#39;".to_string());
}

#[test]
fn owned_when_changed() {
    check!(r#""x&y""#, matches!(escape_html("x&y"), std::borrow::Cow::Owned(_)), true);
}

#[test]
fn unicode() {
    check!(r#""é<é""#, escape_html("é<é").into_owned(), "é&lt;é".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, matches!(escape_html(""), std::borrow::Cow::Borrowed("")), true);
}
