use solution::*;

#[test]
fn whole() {
    check!(r#""abc", "abc""#, after("abc", "abc"), Some(""));
}
