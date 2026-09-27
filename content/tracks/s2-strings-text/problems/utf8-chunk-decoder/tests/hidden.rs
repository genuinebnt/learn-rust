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
fn nothing() {
    check!(r#"no chunks"#, decode(&[]), String::new());
}

#[test]
fn empty_chunks() {
    check!(r#"[], b"a", []"#, decode(&[&[], b"a", &[]]), "a".to_string());
}

#[test]
fn split_then_bad_continuation() {
    check!(r#"[0xE2] then b"A""#, decode(&[&[0xE2], b"A"]), "\u{FFFD}A".to_string());
}

#[test]
fn two_bytes_of_three_then_bad() {
    check!(r#"[0xE2, 0x82] then b"A""#, decode(&[&[0xE2, 0x82], b"A"]), "\u{FFFD}A".to_string());
}

#[test]
fn completes_and_leaves_a_new_tail() {
    check!(r#"[0xC3], [0xA9, 0xE6], [0x97, 0xA5]"#, decode(&[&[0xC3], &[0xA9, 0xE6], &[0x97, 0xA5]]), "é日".to_string());
}

#[test]
fn tail_then_text() {
    check!(r#"[0xF0, 0x9F] then [0xA6, 0x80, b'x']"#, decode(&[&[0xF0, 0x9F], &[0xA6, 0x80, b'x']]), "🦀x".to_string());
}

#[test]
fn surrogate_bytes() {
    check!(r#"[0xED, 0xA0, 0x80]"#, decode(&[&[0xED, 0xA0, 0x80]]), "\u{FFFD}\u{FFFD}\u{FFFD}".to_string());
}

#[test]
fn overlong_encoding() {
    check!(r#"[0xC0, 0x80]"#, decode(&[&[0xC0, 0x80]]), "\u{FFFD}\u{FFFD}".to_string());
}

#[test]
fn stray_continuation_bytes() {
    check!(r#"[0x80, 0x80] then b"ok""#, decode(&[&[0x80, 0x80], b"ok"]), "\u{FFFD}\u{FFFD}ok".to_string());
}

#[test]
fn lead_byte_then_lead_byte() {
    check!(r#"[0xC3] then [0xC3, 0xA9]"#, decode(&[&[0xC3], &[0xC3, 0xA9]]), "\u{FFFD}é".to_string());
}

#[test]
fn invalid_then_split() {
    check!(r#"b"\xff\xc3" then [0xA9]"#, decode(&[b"\xff\xc3", &[0xA9]]), "\u{FFFD}é".to_string());
}

#[test]
fn output_is_appended() {
    let mut d = Utf8Decoder::new();
    let mut out = String::from("> ");
    d.push(&[0xC3], &mut out);
    d.push(&[0xA9], &mut out);
    d.finish(&mut out);
    check!(r#"out already holds "> ""#, out, "> é".to_string());
}

#[test]
fn nothing_emitted_until_complete() {
    let mut d = Utf8Decoder::new();
    let mut out = String::new();
    d.push(&[0xE6, 0x97], &mut out);
    check!(r#"after pushing only [0xE6, 0x97]"#, out, String::new());
}

#[test]
fn random_vs_from_utf8_lossy() {
    let mut rng = anneal_prelude::Rng::new(7216);
    let alphabet = [0x41u8, 0xC3, 0xA9, 0xE6, 0x97, 0xA5, 0xF0, 0x9F, 0xA6, 0x80, 0xFF, 0xED, 0xA0, 0xC0];
    for _ in 0..500 {
        let len = rng.below(16);
        let bytes: Vec<u8> = (0..len).map(|_| *rng.pick(&alphabet)).collect();
        let mut cuts: Vec<usize> = (0..rng.below(5)).map(|_| rng.below(len + 1)).collect();
        cuts.sort();
        let mut chunks: Vec<&[u8]> = Vec::new();
        let mut at = 0;
        for &c in &cuts {
            chunks.push(&bytes[at..c]);
            at = c;
        }
        chunks.push(&bytes[at..]);
        check!(format!("chunks = {chunks:x?}"), decode(&chunks), String::from_utf8_lossy(&bytes).into_owned());
    }
}

#[test]
fn scale_1mb_in_small_chunks() {
    let text = "aé日🦀".repeat(100_000);
    let bytes = text.as_bytes();
    for size in [1, 3, 7] {
        let chunks: Vec<&[u8]> = bytes.chunks(size).collect();
        check!(format!("\"aé日🦀\" × 100000 in {size}-byte chunks"), decode(&chunks) == text, true);
    }
}
