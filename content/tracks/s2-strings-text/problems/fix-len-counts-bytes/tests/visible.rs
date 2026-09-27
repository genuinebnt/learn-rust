use solution::*;

#[test]
fn ascii() {
    check!(r#""ab", 6, '*'"#, center("ab", 6, '*'), "**ab**".to_string());
}

#[test]
fn accented() {
    check!(r#""né", 4, '.'"#, center("né", 4, '.'), ".né.".to_string());
}
