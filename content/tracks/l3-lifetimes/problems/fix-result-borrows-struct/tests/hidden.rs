use solution::*;

#[test]
fn tie() {
    check!(r#""ab\ncd""#, Document::new("ab\ncd").longest_line(), "ab");
}
