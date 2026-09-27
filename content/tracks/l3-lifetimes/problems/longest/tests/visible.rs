use solution::*;

#[test]
fn longer_first() {
    check!(r#""apple", "fig""#, longest("apple", "fig"), "apple");
}

#[test]
fn tie() {
    check!(r#""ab", "cd""#, longest("ab", "cd"), "ab");
}

#[test]
fn longer_second() {
    check!(r#""abc", "abcd""#, longest("abc", "abcd"), "abcd");
}

#[test]
fn both_empty() {
    check!(r#""", """#, longest("", ""), "");
}

#[test]
fn one_empty() {
    check!(r#""", "a""#, longest("", "a"), "a");
}
