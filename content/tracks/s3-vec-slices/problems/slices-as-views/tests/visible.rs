use solution::*;

#[test]
fn parse_with_magic() {
    check!(r#"b"TLV\x01\x02hi\x07\x00""#, parse_tlv(b"TLV\x01\x02hi\x07\x00"), Some(vec![(1, &b"hi"[..]), (7, &b""[..])]));
}

#[test]
fn parse_truncated_value() {
    check!(r#"b"\x01\x05abc""#, parse_tlv(b"\x01\x05abc"), None);
}

#[test]
fn parse_empty() {
    check!(r#"b"" and b"TLV""#, (parse_tlv(b""), parse_tlv(b"TLV")), (Some(vec![]), Some(vec![])));
}

#[test]
fn encode_round_trip() {
    check!(r#"[(1, b"hi"), (2, b"")]"#, encode_tlv(&[(1, b"hi"), (2, b"")]), Some(b"\x01\x02hi\x02\x00".to_vec()));
}

#[test]
fn join_with_separator() {
    check!(r#"[(1, b"ab"), (2, b""), (3, b"c")], sep = b'/'"#, join_values(&[(1, b"ab"), (2, b""), (3, b"c")], b'/'), b"ab//c".to_vec());
}
