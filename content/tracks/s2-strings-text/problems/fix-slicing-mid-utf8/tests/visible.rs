use solution::*;

#[test]
fn ascii() {
    check!(r#""hello", 3"#, prefix("hello", 3), "hel");
}

#[test]
fn accented() {
    check!(r#""héllo", 2"#, prefix("héllo", 2), "hé");
}
