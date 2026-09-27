use solution::*;

#[test]
fn tabs_replaced() {
    check!(r#"normalize("a\tb")"#, normalize("a\tb"), "a    b");
}

#[test]
fn trim_only_borrows() {
    use std::borrow::Cow;
    check!(r#"normalize("plain   ") is a borrowed slice"#, matches!(normalize("plain   "), Cow::Borrowed("plain")), true);
}

#[test]
fn trailing_tab_is_trimmed_not_replaced() {
    use std::borrow::Cow;
    check!(r#"normalize("x \t") borrows "x""#, matches!(normalize("x \t"), Cow::Borrowed("x")), true);
}

#[test]
fn newline_added() {
    use std::borrow::Cow;
    check!(r#"with_newline(Borrowed("hi"))"#, with_newline(Cow::Borrowed("hi")), "hi\n");
}

#[test]
fn newline_kept_borrowed() {
    use std::borrow::Cow;
    check!(r#"with_newline(Borrowed("done\n")) stays borrowed"#, matches!(with_newline(Cow::Borrowed("done\n")), Cow::Borrowed("done\n")), true);
}
