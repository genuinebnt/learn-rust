use solution::*;

#[test]
fn tabs() {
    check!(r#""a\tb""#, normalize("a\tb"), "a    b");
}

#[test]
fn no_tabs_borrowed() {
    check!(r#""plain""#, matches!(normalize("plain"), std::borrow::Cow::Borrowed("plain")), true);
}
