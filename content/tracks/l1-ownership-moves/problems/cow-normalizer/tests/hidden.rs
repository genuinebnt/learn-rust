use solution::*;

#[test]
fn empty() {
    use std::borrow::Cow;
    check!(r#"normalize("")"#, matches!(normalize(""), Cow::Borrowed("")), true);
}

#[test]
fn only_whitespace() {
    use std::borrow::Cow;
    check!(r#"normalize(" \t \n")"#, matches!(normalize(" \t \n"), Cow::Borrowed("")), true);
}

#[test]
fn leading_tab_kept() {
    check!(r#"normalize("\tx  ")"#, normalize("\tx  "), "    x");
}

#[test]
fn consecutive_tabs() {
    check!(r#"normalize("a\t\tb")"#, normalize("a\t\tb"), "a        b");
}

#[test]
fn not_tab_stops() {
    check!(r#"normalize("abc\td")"#, normalize("abc\td"), "abc    d");
}

#[test]
fn borrowed_points_into_input() {
    use std::borrow::Cow;
    let s = String::from("no tabs here  ");
    check!(r#"normalize(String "no tabs here  ")"#, match normalize(&s) { Cow::Borrowed(b) => b.as_ptr() == s.as_ptr() && b.len() == 12, Cow::Owned(_) => false }, true);
}

#[test]
fn leading_space_kept() {
    check!(r#"normalize("  x")"#, normalize("  x"), "  x");
}

#[test]
fn unicode_around_tab() {
    check!(r#"normalize("é\t日 ")"#, normalize("é\t日 "), "é    日");
}

#[test]
fn owned_line_same_buffer() {
    use std::borrow::Cow;
    let mut line = String::with_capacity(16);
    line.push_str("abc");
    let ptr = line.as_ptr();
    check!(r#"with_newline(Owned) pushes onto the same buffer"#, { let out = with_newline(Cow::Owned(line)); (out.as_ptr() == ptr, out.into_owned()) }, (true, "abc\n".to_string()));
}

#[test]
fn owned_with_newline_untouched() {
    use std::borrow::Cow;
    let line = String::from("x\n");
    let ptr = line.as_ptr();
    check!(r#"with_newline(Owned("x\n")) is the same String"#, { let out = with_newline(Cow::Owned(line)); matches!(out, Cow::Owned(_)) && out.as_ptr() == ptr }, true);
}

#[test]
fn empty_line_gets_newline() {
    use std::borrow::Cow;
    check!(r#"with_newline(Borrowed(""))"#, with_newline(Cow::Borrowed("")), "\n");
}

#[test]
fn chained() {
    check!(r#"with_newline(normalize("a\t "))"#, with_newline(normalize("a\t ")), "a\n");
}

use std::borrow::Cow;

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6108);
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "ab é\t\n");
        let trimmed = s.trim_end();
        let want: String = trimmed.chars().map(|c| if c == '\t' { "    ".to_string() } else { c.to_string() }).collect();
        let out = normalize(&s);
        let borrowed = matches!(out, Cow::Borrowed(_));
        check!(format!("normalize({s:?})"), (out.into_owned(), borrowed), (want, !trimmed.contains('\t')));
        let n = rng.below(4);
        let line = rng.string(n, "a\n");
        let ends = line.ends_with('\n');
        let out = with_newline(Cow::Borrowed(&line));
        let want = if ends { line.clone() } else { format!("{line}\n") };
        check!(format!("with_newline(Borrowed({line:?}))"), (matches!(out, Cow::Borrowed(_)), out.into_owned()), (ends, want));
    }
}

#[test]
fn scale_1m_tabs() {
    let s = "\t".repeat(1_000_000) + "x";
    let out = normalize(&s);
    check!("s = 1000000 tabs then x", (out.len(), out.ends_with("    x")), (4_000_001, true));
}
