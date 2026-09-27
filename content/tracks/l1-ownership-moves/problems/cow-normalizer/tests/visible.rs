use solution::*;

#[test]
fn tabs() {
    check!(r#""a\tb""#, normalize("a\tb"), "a    b");
}

#[test]
fn no_tabs_borrowed() {
    check!(r#""plain""#, matches!(normalize("plain"), std::borrow::Cow::Borrowed("plain")), true);
}

#[test]
fn two_tabs() {
    check!(r#""\tx\t""#, normalize("\tx\t"), "    x    ");
}

#[test]
fn empty_visible() {
    check!(r#""""#, normalize(""), "");
}

#[test]
fn changed_is_owned() {
    check!(r#""x\ty""#, matches!(normalize("x\ty"), std::borrow::Cow::Owned(_)), true);
}
