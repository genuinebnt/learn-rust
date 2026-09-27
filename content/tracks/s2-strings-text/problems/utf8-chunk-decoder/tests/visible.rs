use solution::*;

/// Feeds `chunks` through one decoder, then finishes it.
fn decode(chunks: &[&[u8]]) -> String {
    let mut d = Utf8Decoder::new();
    let mut out = String::new();
    for c in chunks {
        d.push(c, &mut out);
    }
    d.finish(&mut out);
    out
}

#[test]
fn whole_chunk() {
    check!(r#"b"hello""#, decode(&[b"hello"]), "hello".to_string());
}

#[test]
fn char_split_in_two() {
    check!(r#"[0xC3] then [0xA9]"#, decode(&[&[0xC3], &[0xA9]]), "é".to_string());
}

#[test]
fn invalid_byte_replaced() {
    check!(r#"b"a\xffb""#, decode(&[b"a\xffb"]), "a\u{FFFD}b".to_string());
}

#[test]
fn unfinished_at_the_end() {
    check!(r#"b"ab\xe2\x82", then finish"#, decode(&[b"ab\xe2\x82"]), "ab\u{FFFD}".to_string());
}

#[test]
fn emoji_one_byte_at_a_time() {
    check!(r#"🦀 as four 1-byte chunks"#, decode(&[&[0xF0], &[0x9F], &[0xA6], &[0x80]]), "🦀".to_string());
}
