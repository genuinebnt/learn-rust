use solution::*;

#[test]
fn none() {
    check!(r#"[]"#, first_lines(&[]).len(), 0);
}

#[test]
fn empty_doc() {
    check!(r#"[""]"#, first_lines(&[String::new()]), vec![String::new()]);
}

#[test]
fn inner_spaces_kept() {
    check!(r#"["a b \nc"]"#, first_lines(&["a b \nc".to_string()]), vec!["a b ".to_string()]);
}

#[test]
fn crlf() {
    check!(r#"["a\r\nb"]"#, first_lines(&["a\r\nb".to_string()]), vec!["a".to_string()]);
}

#[test]
fn unicode_whitespace() {
    check!(r#"["\u{3000}x\u{3000}"]"#, first_lines(&["\u{3000}x\u{3000}".to_string()]), vec!["x".to_string()]);
}

#[test]
fn tabs() {
    check!(r#"["\t\tx\ty"]"#, first_lines(&["\t\tx\ty".to_string()]), vec!["x\ty".to_string()]);
}

#[test]
fn order_kept() {
    check!(r#"["b", "a", "c"]"#, first_lines(&["b".to_string(), "a".to_string(), "c".to_string()]), vec!["b".to_string(), "a".to_string(), "c".to_string()]);
}

#[test]
fn many_docs() {
    let docs: Vec<String> = (0..1000).map(|i| format!("  {i}\nrest")).collect();
    check!(r#"1000 docs "  n\nrest""#, first_lines(&docs), (0..1000).map(|i| i.to_string()).collect::<Vec<_>>());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(307);
    for _ in 0..300 {
        let n = rng.below(4);
        let docs: Vec<String> = (0..n).map(|_| { let len = rng.below(8); rng.string(len, "a \n") }).collect();
        let want: Vec<String> = docs.iter().map(|d| d.trim().split('\n').next().unwrap_or("").to_string()).collect();
        check!(format!("docs = {docs:?}"), first_lines(&docs), want);
    }
}
