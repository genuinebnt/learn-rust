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
fn special_at_end() {
    check!(r#""abc>""#, escape_html("abc>").into_owned(), "abc&gt;".to_string());
}

#[test]
fn special_at_start() {
    check!(r#""<abc""#, escape_html("<abc").into_owned(), "&lt;abc".to_string());
}

#[test]
fn consecutive() {
    check!(r#""<<>>""#, escape_html("<<>>").into_owned(), "&lt;&lt;&gt;&gt;".to_string());
}

#[test]
fn single_quote() {
    check!(r#""'""#, escape_html("'").into_owned(), "&#39;".to_string());
}

#[test]
fn unicode_borrowed() {
    check!(r#""日本語 ✓""#, matches!(escape_html("日本語 ✓"), std::borrow::Cow::Borrowed(_)), true);
}

#[test]
fn borrowed_same_pointer() {
    let s = String::from("no specials here");
    check!(r#""no specials here""#, escape_html(&s).as_ptr() == s.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2212);
    for _ in 0..300 {
        let len = rng.below(10);
        let s = rng.string(len, "a é&<>\"'");
        let mut want = String::new();
        for c in s.chars() {
            match c {
                '&' => want += "&amp;",
                '<' => want += "&lt;",
                '>' => want += "&gt;",
                '"' => want += "&quot;",
                '\'' => want += "&#39;",
                _ => want.push(c),
            }
        }
        let out = escape_html(&s);
        let borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
        check!(format!("s = {s:?}"), (out.into_owned(), borrowed), (want.clone(), want == s));
    }
}

#[test]
fn scale_200k() {
    let s = "a<b&".repeat(50_000);
    let out = escape_html(&s);
    check!("s = \"a<b&…\" (200000 chars)", (out.len(), &out[..12]), (550_000, "a&lt;b&amp;a"));
}
