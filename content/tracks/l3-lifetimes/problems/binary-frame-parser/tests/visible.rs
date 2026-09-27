use solution::*;

#[test]
fn one_frame() {
    let mut buf = b"AN\x01".to_vec();
    buf.extend_from_slice(&5u16.to_be_bytes());
    buf.extend_from_slice(b"hellotail");
    check!(r#"AN, kind 1, len 5, "hello", then "tail""#, parse_frame(&buf), Some((Frame { kind: 1, payload: &b"hello"[..] }, &b"tail"[..])));
}

#[test]
fn bad_magic() {
    check!(r#"b"XX\x01\x00\x00""#, parse_frame(b"XX\x01\x00\x00"), None);
}
