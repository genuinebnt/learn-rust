use solution::*;

#[test]
fn first() {
    check!(r#"word = "rust", i = 0"#, nth_letter("rust", 0), Some('r'));
}

#[test]
fn crab() {
    check!(r#"word = "a🦀b", i = 1"#, nth_letter("a🦀b", 1), Some('🦀'));
}

#[test]
fn after_crab() {
    check!(r#"word = "a🦀b", i = 2"#, nth_letter("a🦀b", 2), Some('b'));
}

#[test]
fn byte_length_is_not_char_length() {
    check!(r#"word = "héllo", i = 5 (6 bytes, 5 characters)"#, nth_letter("héllo", 5), None);
}

#[test]
fn huge_index() {
    check!(r#"word = "abc", i = usize::MAX"#, nth_letter("abc", usize::MAX), None);
}

#[test]
fn cjk() {
    check!(r#"word = "日本語", i = 2"#, nth_letter("日本語", 2), Some('語'));
}

#[test]
fn space() {
    check!(r#"word = "a b", i = 1"#, nth_letter("a b", 1), Some(' '));
}

#[test]
fn single() {
    check!(r#"word = "x", i = 0"#, nth_letter("x", 0), Some('x'));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1003);
    for _ in 0..300 {
        let len = rng.below(6);
        let word = rng.string(len, "aé🦀z");
        let i = rng.below(8);
        let chars: Vec<char> = word.chars().collect();
        check!(format!("word = {word:?}, i = {i}"), nth_letter(&word, i), chars.get(i).copied());
    }
}
