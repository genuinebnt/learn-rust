use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀x""#, reverse_each_word("🦀x"), "x🦀".to_string());
}

#[test]
fn extra_spaces() {
    check!(r#""  a   bc ""#, reverse_each_word("  a   bc "), "a cb".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, reverse_each_word(""), String::new());
}

#[test]
fn only_spaces() {
    check!(r#""   ""#, reverse_each_word("   "), String::new());
}

#[test]
fn tabs_and_newlines() {
    check!(r#""ab\tcd\nef""#, reverse_each_word("ab\tcd\nef"), "ba dc fe".to_string());
}

#[test]
fn palindrome() {
    check!(r#""abba x""#, reverse_each_word("abba x"), "abba x".to_string());
}

#[test]
fn cjk() {
    check!(r#""日本語 テスト""#, reverse_each_word("日本語 テスト"), "語本日 トステ".to_string());
}

#[test]
fn single_char() {
    check!(r#""a""#, reverse_each_word("a"), "a".to_string());
}

#[test]
fn punctuation_moves() {
    check!(r#""a1! b2?""#, reverse_each_word("a1! b2?"), "!1a ?2b".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2211);
    for _ in 0..300 {
        let len = rng.below(14);
        let s = rng.string(len, "abé🦀  \t");
        let mut words: Vec<String> = Vec::new();
        let mut cur: Vec<char> = Vec::new();
        for c in s.chars().chain(std::iter::once(' ')) {
            if c.is_whitespace() {
                if !cur.is_empty() {
                    cur.reverse();
                    words.push(cur.iter().collect());
                    cur.clear();
                }
            } else {
                cur.push(c);
            }
        }
        check!(format!("s = {s:?}"), reverse_each_word(&s), words.join(" "));
    }
}

#[test]
fn scale_200k_words() {
    let s = "abc ".repeat(200_000);
    let out = reverse_each_word(&s);
    check!("s = \"abc abc …\" (200000 words)", (out.len(), &out[..7]), (799_999, "cba cba"));
}
