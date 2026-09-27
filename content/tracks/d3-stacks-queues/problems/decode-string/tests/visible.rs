use solution::*;

#[test]
fn flat() {
    check!(r#""3[a]2[bc]""#, decode_string("3[a]2[bc]"), "aaabcbc".to_string());
}

#[test]
fn nested() {
    check!(r#""3[a2[c]]""#, decode_string("3[a2[c]]"), "accaccacc".to_string());
}

#[test]
fn tail() {
    check!(r#""2[abc]3[cd]ef""#, decode_string("2[abc]3[cd]ef"), "abcabccdcdcdef".to_string());
}

#[test]
fn two_digits() {
    check!(r#""10[a]""#, decode_string("10[a]"), "a".repeat(10));
}

#[test]
fn plain() {
    check!(r#""abc""#, decode_string("abc"), "abc".to_string());
}
