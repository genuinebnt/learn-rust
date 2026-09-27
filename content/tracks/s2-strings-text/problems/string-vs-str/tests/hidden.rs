use solution::*;

#[test]
fn dot_in_directory() {
    check!(r#""v1.2/README""#, extension("v1.2/README"), None);
}

#[test]
fn trailing_dot() {
    check!(r#""notes.""#, extension("notes."), None);
}

#[test]
fn hidden_file_with_extension() {
    check!(r#""dir/.env.local""#, extension("dir/.env.local"), Some("local"));
}

#[test]
fn extension_edge_names() {
    check!(r#""", "/", "..", "a/b/""#, [extension(""), extension("/"), extension(".."), extension("a/b/")], [None; 4]);
}

#[test]
fn double_dot() {
    check!(r#""a..b""#, extension("a..b"), Some("b"));
}

#[test]
fn unicode_extension() {
    check!(r#""文書/報告.テキスト""#, extension("文書/報告.テキスト"), Some("テキスト"));
}

#[test]
fn extension_borrows_input() {
    let s = String::from("a/b.rs");
    check!(r#"extension points into its input"#, extension(&s).map(|e| e.as_ptr()) == Some(s[4..].as_ptr()), true);
}

#[test]
fn lone_quote_is_not_a_pair() {
    check!(r#""\"""#, unquote("\""), "\"");
}

#[test]
fn empty_quotes() {
    check!(r#""\"\"" and "''""#, (unquote("\"\""), unquote("''")), ("", ""));
}

#[test]
fn only_one_pair_removed() {
    check!(r#""\"\"a\"\"""#, unquote("\"\"a\"\""), "\"a\"");
}

#[test]
fn mismatched_quotes() {
    check!(r#""\"a'" and "'a\"""#, (unquote("\"a'"), unquote("'a\"")), ("\"a'", "'a\""));
}

#[test]
fn inner_quotes_kept() {
    check!(r#""'it\"s'""#, unquote("'it\"s'"), "it\"s");
}

#[test]
fn unicode_quotes_untouched() {
    check!(r#""«x»" and "é""#, (unquote("«x»"), unquote("é")), ("«x»", "é"));
}

#[test]
fn unquote_borrows_input() {
    let s = String::from("'abc'");
    check!(r#"unquote points into its input"#, unquote(&s).as_ptr() == s[1..].as_ptr(), true);
}

#[test]
fn second_param() {
    let mut u = String::from("http://h/p?a=1");
    add_param(&mut u, "b", "2");
    check!(r#"url = "http://h/p?a=1", key = "b", value = "2""#, u, "http://h/p?a=1&b=2".to_string());
}

#[test]
fn query_ends_with_question_mark() {
    let mut u = String::from("http://h/p?");
    add_param(&mut u, "k", "v");
    check!(r#"url = "http://h/p?", key = "k", value = "v""#, u, "http://h/p?k=v".to_string());
}

#[test]
fn query_ends_with_ampersand() {
    let mut u = String::from("http://h/p?a=1&");
    add_param(&mut u, "k", "v");
    check!(r#"url = "http://h/p?a=1&", key = "k", value = "v""#, u, "http://h/p?a=1&k=v".to_string());
}

#[test]
fn question_mark_in_fragment() {
    let mut u = String::from("http://h/p#a?b");
    add_param(&mut u, "k", "v");
    check!(r#"url = "http://h/p#a?b", key = "k", value = "v""#, u, "http://h/p?k=v#a?b".to_string());
}

#[test]
fn empty_fragment() {
    let mut u = String::from("http://h/#");
    add_param(&mut u, "k", "");
    check!(r#"url = "http://h/#", key = "k", value = """#, u, "http://h/?k=#".to_string());
}

#[test]
fn unicode_value() {
    let mut u = String::from("http://h/");
    add_param(&mut u, "q", "café");
    check!(r#"url = "http://h/", key = "q", value = "café""#, u, "http://h/?q=café".to_string());
}

#[test]
fn add_twice() {
    let mut u = String::from("http://h");
    add_param(&mut u, "a", "1");
    add_param(&mut u, "b", "2");
    check!(r#""http://h" + a=1 + b=2"#, u, "http://h?a=1&b=2".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7201);
    for _ in 0..400 {
        let len = rng.below(9);
        let path = rng.string(len, "a./é");
        let name = match path.rfind('/') {
            Some(i) => &path[i + 1..],
            None => &path[..],
        };
        let want_ext = match name.rfind('.') {
            Some(i) if i > 0 && i + 1 < name.len() => Some(&name[i + 1..]),
            _ => None,
        };
        let len = rng.below(6);
        let q = rng.string(len, "a\"'");
        let b = q.as_bytes();
        let want_q = if b.len() >= 2 && (b[0] == b'"' || b[0] == b'\'') && b[b.len() - 1] == b[0] { &q[1..q.len() - 1] } else { &q[..] };
        let len = rng.below(7);
        let url = rng.string(len, "h?&#=");
        let end = url.find('#').unwrap_or(url.len());
        let sep = if !url[..end].contains('?') { "?" } else if url[..end].ends_with('?') || url[..end].ends_with('&') { "" } else { "&" };
        let want_url = format!("{}{sep}k=v{}", &url[..end], &url[end..]);
        let mut got_url = url.clone();
        add_param(&mut got_url, "k", "v");
        check!(format!("path = {path:?}, s = {q:?}, url = {url:?}"), (extension(&path), unquote(&q), got_url), (want_ext, want_q, want_url));
    }
}
