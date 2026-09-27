use solution::*;

#[test]
fn flat() {
    check!(r#""3[a]2[bc]""#, decode_string("3[a]2[bc]"), "aaabcbc".to_string());
}

#[test]
fn nested() {
    check!(r#""3[a2[c]]""#, decode_string("3[a2[c]]"), "accaccacc".to_string());
}
