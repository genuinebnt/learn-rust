use solution::*;

#[test]
fn all_five() {
    check!(r#""&<>\"'""#, escape_html("&<>\"'").into_owned(), "&amp;&lt;&gt;&quot;&#39;".to_string());
}

#[test]
fn owned_when_changed() {
    check!(r#""x&y""#, matches!(escape_html("x&y"), std::borrow::Cow::Owned(_)), true);
}

#[test]
fn unicode() {
    check!(r#""é<é""#, escape_html("é<é").into_owned(), "é&lt;é".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, matches!(escape_html(""), std::borrow::Cow::Borrowed("")), true);
}

#[test]
fn special_at_ends() {
    check!(r#""<abc>""#, escape_html("<abc>").into_owned(), "&lt;abc&gt;".to_string());
}

#[test]
fn borrowed_same_pointer() {
    let s = String::from("no specials here");
    check!(r#""no specials here""#, escape_html(&s).as_ptr() == s.as_ptr(), true);
}

#[test]
fn borrow_allocates_nothing() {
    let (out, n) = anneal_prelude::allocs(|| escape_html("日本語 ✓"));
    check!(r#""日本語 ✓""#, (matches!(out, std::borrow::Cow::Borrowed(_)), n.count), (true, 0));
}

#[test]
fn escape_allocates_once() {
    let (out, n) = anneal_prelude::allocs(|| escape_html("a<b"));
    check!(r#""a<b""#, (out.into_owned(), n.count), ("a&lt;b".to_string(), 1));
}

#[test]
fn bytes_borrow_allocates_nothing() {
    let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"ok"));
    check!(r#"b"ok""#, (out, n.count), (std::borrow::Cow::Borrowed("ok"), 0));
}

#[test]
fn bytes_valid_but_escaped() {
    let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"a&b"));
    check!(r#"b"a&b""#, (out.into_owned(), n.count), ("a&amp;b".to_string(), 1));
}

#[test]
fn bytes_invalid_no_extra_copy() {
    let (_, lossy) = anneal_prelude::allocs(|| String::from_utf8_lossy(b"a\xffb"));
    let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"a\xffb"));
    check!(r#"b"a\xffb": no allocation beyond from_utf8_lossy's"#, (out.into_owned(), n.count), ("a\u{FFFD}b".to_string(), lossy.count));
}

#[test]
fn bytes_invalid_and_escaped() {
    let (_, lossy) = anneal_prelude::allocs(|| String::from_utf8_lossy(b"<\xff"));
    let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"<\xff"));
    check!(r#"b"<\xff": from_utf8_lossy's allocations plus one"#, (out.into_owned(), n.count), ("&lt;\u{FFFD}".to_string(), lossy.count + 1));
}

#[test]
fn bytes_truncated_sequence() {
    check!(r#"b"x\xe2\x82""#, escape_bytes(b"x\xe2\x82").into_owned(), "x\u{FFFD}".to_string());
}

#[test]
fn bytes_empty() {
    check!(r#"b"""#, matches!(escape_bytes(b""), std::borrow::Cow::Borrowed("")), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7211);
    let pieces: [&[u8]; 8] = [b"a", "é".as_bytes(), b"&", b"<", b"'", b"\xff", b"\xc3", b"\""];
    for _ in 0..400 {
        let mut bytes = Vec::new();
        for _ in 0..rng.below(8) {
            bytes.extend_from_slice(*rng.pick(&pieces));
        }
        let text = String::from_utf8_lossy(&bytes).into_owned();
        let mut want = String::new();
        for c in text.chars() {
            match c {
                '&' => want += "&amp;",
                '<' => want += "&lt;",
                '>' => want += "&gt;",
                '"' => want += "&quot;",
                '\'' => want += "&#39;",
                _ => want.push(c),
            }
        }
        let borrowed = std::str::from_utf8(&bytes).map_or(false, |s| s == want);
        let out = escape_bytes(&bytes);
        let got_borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
        let html = std::str::from_utf8(&bytes).ok().map(|s| escape_html(s).into_owned());
        check!(format!("bytes = {bytes:?}"), (out.into_owned(), got_borrowed, html.clone()), (want.clone(), borrowed, html.map(|_| want)));
    }
}

#[test]
fn scale_200k() {
    let s = "a<b&".repeat(50_000);
    let out = escape_html(&s);
    check!("s = \"a<b&…\" (200000 chars)", (out.len(), &out[..12]), (550_000, "a&lt;b&amp;a"));
}
