use solution::*;

#[test]
fn mixed() {
    check!(r#""()[]{}""#, is_valid("()[]{}"), true);
}

#[test]
fn wrong_kind() {
    check!(r#""(]""#, is_valid("(]"), false);
}

#[test]
fn nested() {
    check!(r#""{[]}""#, is_valid("{[]}"), true);
}

#[test]
fn one_pair() {
    check!(r#""()""#, is_valid("()"), true);
}

#[test]
fn nested_mixed() {
    check!(r#""([])""#, is_valid("([])"), true);
}

#[test]
fn interleaved() {
    check!(r#""([)]""#, is_valid("([)]"), false);
}

#[test]
fn empty() {
    check!(r#""""#, is_valid(""), true);
}
