use solution::*;

#[test]
fn tabs_owned() {
    check!(r#""\t""#, matches!(normalize("\t"), std::borrow::Cow::Owned(_)), true);
}

#[test]
fn empty() {
    check!(r#""""#, normalize(""), "");
}

#[test]
fn empty_borrowed() {
    check!(r#""""#, matches!(normalize(""), std::borrow::Cow::Borrowed("")), true);
}

#[test]
fn only_tab() {
    check!(r#""\t""#, normalize("\t"), "    ");
}

#[test]
fn consecutive_tabs() {
    check!(r#""a\t\tb""#, normalize("a\t\tb"), "a        b");
}

#[test]
fn not_tab_stops() {
    check!(r#""abc\td" (always four spaces, not to the next tab stop)"#, normalize("abc\td"), "abc    d");
}

#[test]
fn unicode_around_tab() {
    check!(r#""é\t日""#, normalize("é\t日"), "é    日");
}

#[test]
fn other_whitespace_kept() {
    check!(r#""a\nb \r""#, matches!(normalize("a\nb \r"), std::borrow::Cow::Borrowed("a\nb \r")), true);
}

#[test]
fn borrowed_same_pointer() {
    check!(r#""no tabs here""#, { let s = String::from("no tabs here"); let out = normalize(&s); out.as_ptr() == s.as_ptr() }, true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1109);
    for _ in 0..300 {
        let len = rng.below(12);
        let s = rng.string(len, "ab é\t");
        let mut want = String::new();
        for c in s.chars() {
            if c == '\t' {
                want.push_str("    ");
            } else {
                want.push(c);
            }
        }
        let out = normalize(&s);
        let borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
        check!(format!("s = {s:?}"), (out.into_owned(), borrowed), (want, !s.contains('\t')));
    }
}

#[test]
fn scale_1m_tabs() {
    let s = "\t".repeat(1_000_000);
    let out = normalize(&s);
    check!("s = 1000000 tabs", (out.len(), out.bytes().all(|b| b == b' ')), (4_000_000, true));
}
