use solution::*;

#[test]
fn truncated_payload() {
    check!(r#"length 5, only 3 bytes"#, parse_frame(b"AN\x01\x00\x05abc"), None);
}

#[test]
fn length_is_big_endian() {
    let mut buf = b"AN\x09\x01\x00".to_vec();
    buf.resize(5 + 256, 7);
    check!(r#"length bytes [0x01, 0x00] = 256, 256 payload bytes"#, parse_frame(&buf).map(|(f, rest)| (f.payload.len(), rest.len())), Some((256, 0)));
}

#[test]
fn exact_fit() {
    check!(r#"length 2, exactly 2 bytes"#, parse_frame(b"AN\x03\x00\x02hi"), Some((Frame { kind: 3, payload: &b"hi"[..] }, &[][..])));
}

#[test]
fn kind_255() {
    check!(r#"kind 0xFF"#, parse_frame(b"AN\xff\x00\x00").map(|(f, _)| f.kind), Some(255));
}

#[test]
fn only_magic() {
    check!(r#"b"AN""#, parse_frame(b"AN"), None);
}

#[test]
fn second_frame_truncated() {
    check!(r#"a whole frame, then a frame missing its payload"#, parse_all(b"AN\x01\x00\x00AN\x02\x00\x03ab"), None);
}

#[test]
fn magic_case() {
    check!(r#"b"an\x01\x00\x00""#, parse_frame(b"an\x01\x00\x00"), None);
}

#[test]
fn max_length_frame() {
    let mut buf = b"AN\x01\xff\xff".to_vec();
    buf.resize(5 + 65_535, 0);
    check!(r#"length 0xFFFF with 65535 bytes"#, parse_all(&buf).map(|v| v[0].payload.len()), Some(65_535));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(311);
    for _ in 0..300 {
        let count = rng.below(4);
        let mut buf = Vec::new();
        let mut want: Vec<(u8, Vec<u8>)> = Vec::new();
        for _ in 0..count {
            let kind = rng.int(0, 255) as u8;
            let len = rng.below(300);
            let payload: Vec<u8> = rng.vec(len, 0, 255);
            buf.extend_from_slice(b"AN");
            buf.push(kind);
            buf.push((len >> 8) as u8);
            buf.push(len as u8);
            buf.extend_from_slice(&payload);
            want.push((kind, payload));
        }
        let got = parse_all(&buf).map(|v| v.iter().map(|f| (f.kind, f.payload.to_vec())).collect::<Vec<_>>());
        check!(format!("{count} random frames"), got, Some(want.clone()));
        // Cutting any whole frame short makes the buffer invalid.
        if !buf.is_empty() {
            let cut = rng.below(buf.len());
            let whole = want.iter().scan(0, |end, (_, p)| { *end += 5 + p.len(); Some(*end) }).any(|end| end == cut);
            let want_cut = if whole || cut == 0 { Some(()) } else { None };
            check!(format!("{count} random frames cut to {cut} bytes"), parse_all(&buf[..cut]).map(|_| ()), want_cut);
        }
    }
}

#[test]
fn scale_100k_frames() {
    let mut buf = Vec::new();
    for i in 0..100_000u32 {
        buf.extend_from_slice(b"AN");
        buf.push((i % 256) as u8);
        buf.extend_from_slice(&1u16.to_be_bytes());
        buf.push((i % 7) as u8);
    }
    let frames = parse_all(&buf).unwrap();
    check!("100000 one-byte frames", (frames.len(), frames[99_999].kind, frames[99_999].payload), (100_000, (99_999 % 256) as u8, &[(99_999 % 7) as u8][..]));
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
