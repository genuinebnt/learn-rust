use solution::*;

#[test]
fn center_accented() {
    check!(r#""né", 4, '.'"#, center("né", 4, '.'), ".né.".to_string());
}

#[test]
fn center_odd_extra_right() {
    check!(r#""a", 4, '*'"#, center("a", 4, '*'), "*a**".to_string());
}

#[test]
fn indent_spaces_and_tabs() {
    check!(r#""  \tx""#, indent("  \tx"), 3);
}

#[test]
fn indent_no_break_spaces() {
    check!(r#""\u{a0}\u{a0}x""#, indent("\u{a0}\u{a0}x"), 2);
}

#[test]
fn wrap_accented_fits() {
    check!(r#""héllo wörld", 11"#, wrap("héllo wörld", 11), vec!["héllo wörld"]);
}
