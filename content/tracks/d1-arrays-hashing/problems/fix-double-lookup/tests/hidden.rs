use solution::*;

#[test]
fn whitespace() {
    check!(r#"text = "  x\n x\tx  ""#, word_counts("  x\n x\tx  "), std::collections::HashMap::from([("x", 3)]));
}

#[test]
fn single_word() {
    check!(r#"text = "hello""#, word_counts("hello"), std::collections::HashMap::from([("hello", 1)]));
}

#[test]
fn only_spaces() {
    check!(r#"text = "   ""#, word_counts("   "), std::collections::HashMap::new());
}

#[test]
fn all_distinct() {
    check!(r#"text = "a b c""#, word_counts("a b c"), std::collections::HashMap::from([("a", 1), ("b", 1), ("c", 1)]));
}

#[test]
fn case_sensitive() {
    check!(r#"text = "Go go GO go""#, word_counts("Go go GO go"), std::collections::HashMap::from([("Go", 1), ("go", 2), ("GO", 1)]));
}

#[test]
fn punctuation_kept() {
    check!(r#"text = "hi, hi""#, word_counts("hi, hi"), std::collections::HashMap::from([("hi,", 1), ("hi", 1)]));
}

#[test]
fn unicode() {
    check!(r#"text = "café 🦀 café""#, word_counts("café 🦀 café"), std::collections::HashMap::from([("café", 2), ("🦀", 1)]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(10);
    let words = ["a", "b", "ab", "ba"];
    let gaps = [" ", "  ", "\t", "\n"];
    for _ in 0..200 {
        let n = rng.below(8);
        let mut text = String::new();
        for _ in 0..n {
            text.push_str(*rng.pick(&gaps));
            text.push_str(*rng.pick(&words));
        }
        let mut want = std::collections::HashMap::new();
        for w in text.split_whitespace() {
            want.insert(w, text.split_whitespace().filter(|x| *x == w).count());
        }
        check!(format!("text = {text:?}"), word_counts(&text), want);
    }
}
