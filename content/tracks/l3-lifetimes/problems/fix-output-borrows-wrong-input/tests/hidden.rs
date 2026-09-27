use solution::*;

#[test]
fn whole() {
    check!(r#""abc", "abc""#, after("abc", "abc"), Some(""));
}

#[test]
fn prefix_longer() {
    check!(r#""ab", "abc""#, after("ab", "abc"), None);
}

#[test]
fn empty_line() {
    check!(r#""", """#, after("", ""), Some(""));
}

#[test]
fn empty_line_nonempty_prefix() {
    check!(r#""", "a""#, after("", "a"), None);
}

#[test]
fn repeated_prefix_removed_once() {
    check!(r#""abab", "ab""#, after("abab", "ab"), Some("ab"));
}

#[test]
fn case_sensitive() {
    check!(r#""Key: v", "key: ""#, after("Key: v", "key: "), None);
}

#[test]
fn unicode() {
    check!(r#""héllo", "hé""#, after("héllo", "hé"), Some("llo"));
}

#[test]
fn borrows_line() {
    let line = String::from("key=value");
    let rest = after(&line, "key=").unwrap();
    check!(r#"result points into line"#, std::ptr::eq(rest.as_ptr(), line[4..].as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(304);
    for _ in 0..300 {
        let (ln, pn) = (rng.below(6), rng.below(4));
        let line = rng.string(ln, "ab");
        let prefix = rng.string(pn, "ab");
        let want = if line.len() >= prefix.len() && line[..prefix.len()] == prefix { Some(&line[prefix.len()..]) } else { None };
        check!(format!("line = {line:?}, prefix = {prefix:?}"), after(&line, &prefix), want);
    }
}
