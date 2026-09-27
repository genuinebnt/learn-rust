use solution::*;

#[test]
fn truncated_payload() {
    check!(r#"length 5, only 3 bytes"#, parse_frame(b"AN\x01\x00\x05abc"), None);
}

#[test]
fn short_header() {
    check!(r#"b"AN\x01\x00""#, parse_frame(b"AN\x01\x00"), None);
}

#[test]
fn empty_payload() {
    check!(r#"length 0"#, parse_frame(b"AN\x07\x00\x00"), Some((Frame { kind: 7, payload: &[][..] }, &[][..])));
}

#[test]
fn zero_copy() {
    let buf = b"AN\x01\x00\x02hi".to_vec();
    let (f, _) = parse_frame(&buf).unwrap();
    let same = std::ptr::eq(f.payload.as_ptr(), buf[5..].as_ptr());
    check!(r#"payload points into buf"#, same, true);
}

#[test]
fn two_frames() {
    check!(r#"two frames back to back"#, parse_all(b"AN\x01\x00\x01aAN\x02\x00\x00").map(|v| v.iter().map(|f| f.kind).collect::<Vec<_>>()), Some(vec![1, 2]));
}

#[test]
fn trailing_junk() {
    check!(r#"one frame then 1 junk byte"#, parse_all(b"AN\x01\x00\x00!"), None);
}

#[test]
fn large_length() {
    check!(r#"length 0xFFFF with 3 bytes"#, parse_frame(b"AN\x01\xff\xffabc"), None);
}
