use solution::*;

#[test]
fn ascii() {
    check!(r#""hello", 3"#, prefix("hello", 3), "hel");
}

#[test]
fn accented() {
    check!(r#""héllo", 2"#, prefix("héllo", 2), "hé");
}

#[test]
fn shorter() {
    check!(r#""hi", 5"#, prefix("hi", 5), "hi");
}

#[test]
fn exact_length() {
    check!(r#""abc", 3"#, prefix("abc", 3), "abc");
}

#[test]
fn empty() {
    check!(r#""", 2"#, prefix("", 2), "");
}
