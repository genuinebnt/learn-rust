use solution::*;

#[test]
fn empty() {
    check!(r#""""#, slug(""), String::new());
}

#[test]
fn only_spaces() {
    check!(r#""   ""#, slug("   "), String::new());
}

#[test]
fn digits() {
    check!(r#""Top 10 List""#, slug("Top 10 List"), "top-10-list".to_string());
}

#[test]
fn hyphens_kept() {
    check!(r#""Pre-Order now""#, slug("Pre-Order now"), "pre-order-now".to_string());
}

#[test]
fn unicode_lowercase() {
    check!(r#""Ünïcode ÉTÉ""#, slug("Ünïcode ÉTÉ"), "ünïcode-été".to_string());
}

#[test]
fn unicode_space() {
    check!(r#""a\u{3000}B""#, slug("a\u{3000}B"), "a-b".to_string());
}

#[test]
fn mixed_case_words() {
    check!(r#""hELLO wORLD""#, slug("hELLO wORLD"), "hello-world".to_string());
}

#[test]
fn already_slug() {
    check!(r#""already-a-slug""#, slug("already-a-slug"), "already-a-slug".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(302);
    for _ in 0..300 {
        let n = rng.below(12);
        let text = rng.string(n, "aB \t");
        let mut want = String::new();
        for w in text.split(|c: char| c == ' ' || c == '\t').filter(|w| !w.is_empty()) {
            if !want.is_empty() {
                want.push('-');
            }
            want.push_str(&w.to_lowercase());
        }
        check!(format!("text = {text:?}"), slug(&text), want);
    }
}
