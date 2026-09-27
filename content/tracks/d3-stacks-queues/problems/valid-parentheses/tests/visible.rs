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
