use solution::*;

#[test]
fn tie_keeps_first() {
    check!(r#"text = "ab cd""#, summarize("ab cd"), (2, "ab".to_string()));
}

#[test]
fn three_way_tie() {
    check!(r#"text = "aa bb cc""#, summarize("aa bb cc"), (3, "aa".to_string()));
}

#[test]
fn longest_last() {
    check!(r#"text = "a bb ccc""#, summarize("a bb ccc"), (3, "ccc".to_string()));
}

#[test]
fn runs_of_spaces() {
    check!(r#"text = "a   bb  c""#, summarize("a   bb  c"), (3, "bb".to_string()));
}

#[test]
fn leading_trailing() {
    check!(r#"text = "  hi  ""#, summarize("  hi  "), (1, "hi".to_string()));
}

#[test]
fn tabs_and_newlines() {
    check!(r#"text = "one\ttwo\nthree""#, summarize("one\ttwo\nthree"), (3, "three".to_string()));
}

#[test]
fn only_whitespace() {
    check!(r#"text = "   ""#, summarize("   "), (0, String::new()));
}

#[test]
fn unicode_bytes() {
    check!(r#"text = "ab ünï" ("ünï" is 5 bytes)"#, summarize("ab ünï"), (2, "ünï".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1101);
    for _ in 0..300 {
        let n = rng.below(24);
        let text = rng.string(n, "ab  \t\n");
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut best = "";
        for w in &words {
            if w.len() > best.len() {
                best = w;
            }
        }
        check!(format!("text = {text:?}"), summarize(&text), (words.len(), best.to_string()));
    }
}

#[test]
fn many_words() {
    let text = "ab ".repeat(100_000) + "abc";
    check!("text = \"ab ab … ab abc\" (100001 words)", summarize(&text), (100_001, "abc".to_string()));
}
