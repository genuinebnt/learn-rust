use solution::*;

#[test]
fn tail() {
    check!(r#""2[abc]3[cd]ef""#, decode_string("2[abc]3[cd]ef"), "abcabccdcdcdef".to_string());
}

#[test]
fn plain() {
    check!(r#""abc""#, decode_string("abc"), "abc".to_string());
}

#[test]
fn two_digits() {
    check!(r#""10[a]""#, decode_string("10[a]"), "a".repeat(10));
}

#[test]
fn zero() {
    check!(r#""0[x]y""#, decode_string("0[x]y"), "y".to_string());
}
