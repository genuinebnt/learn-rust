use solution::*;

#[test]
fn ascii() {
    check!(r#""ab", 6, '*'"#, center("ab", 6, '*'), "**ab**".to_string());
}

#[test]
fn accented() {
    check!(r#""né", 4, '.'"#, center("né", 4, '.'), ".né.".to_string());
}

#[test]
fn even_padding() {
    check!(r#""abcd", 8, '-'"#, center("abcd", 8, '-'), "--abcd--".to_string());
}

#[test]
fn no_padding_needed() {
    check!(r#""abc", 3, '*'"#, center("abc", 3, '*'), "abc".to_string());
}

#[test]
fn odd_extra_right() {
    check!(r#""a", 4, '*'"#, center("a", 4, '*'), "*a**".to_string());
}
