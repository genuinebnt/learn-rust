use solution::*;

#[test]
fn longer_first() {
    check!(r#""apple", "fig""#, longest("apple", "fig"), "apple");
}

#[test]
fn tie() {
    check!(r#""ab", "cd""#, longest("ab", "cd"), "ab");
}
