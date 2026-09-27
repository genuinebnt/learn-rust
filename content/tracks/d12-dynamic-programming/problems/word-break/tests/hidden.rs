use solution::*;

#[test]
fn empty_everything() {
    check!(r#"s = "", words = []"#, word_break("", &[]), true);
}

#[test]
fn single_word() {
    check!(r#"s = "a", words = ["a"]"#, word_break("a", &["a"]), true);
}

#[test]
fn word_longer_than_s() {
    check!(r#"s = "ab", words = ["abc"]"#, word_break("ab", &["abc"]), false);
}

#[test]
fn overlapping_choices() {
    check!(r#"s = "aaaaaaa", words = ["aaaa", "aaa"]"#, word_break("aaaaaaa", &["aaaa", "aaa"]), true);
}

#[test]
fn only_long_words_fit() {
    check!(r#"s = "bb", words = ["a", "b", "bbb", "bbbb"]"#, word_break("bb", &["a", "b", "bbb", "bbbb"]), true);
}

#[test]
fn leftover_char() {
    check!(r#"s = "catsanddogs", words = ["cats", "dog", "sand", "and", "cat"]"#, word_break("catsanddogs", &["cats", "dog", "sand", "and", "cat"]), false);
}

#[test]
fn unicode() {
    check!(r#"s = "日本語", words = ["日本", "語"]"#, word_break("日本語", &["日本", "語"]), true);
}

#[test]
fn unicode_missing_piece() {
    check!(r#"s = "日本語", words = ["日", "語"]"#, word_break("日本語", &["日", "語"]), false);
}

#[test]
fn accented() {
    check!(r#"s = "héllo", words = ["hé", "llo"]"#, word_break("héllo", &["hé", "llo"]), true);
}

#[test]
fn random_vs_brute_force() {
    fn can(s: &str, words: &[String]) -> bool {
        s.is_empty() || words.iter().any(|w| s.starts_with(w.as_str()) && can(&s[w.len()..], words))
    }
    let mut rng = anneal_prelude::Rng::new(1213);
    for _ in 0..400 {
        let len = rng.below(13);
        let s = rng.string(len, "ab");
        let k = rng.int(0, 4) as usize;
        let mut words: Vec<String> = Vec::new();
        for _ in 0..k {
            let wl = rng.int(1, 4) as usize;
            words.push(rng.string(wl, "ab"));
        }
        let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
        check!(format!("s = {s:?}, words = {words:?}"), word_break(&s, &refs), can(&s, &words));
    }
}

#[test]
fn scale_many_ways_to_fail() {
    // Every prefix of a's splits many ways, but the final b never fits.
    let s = format!("{}b", "a".repeat(299));
    let words: Vec<String> = (1..=20).map(|k| "a".repeat(k)).collect();
    let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
    check!("s = \"aaa…ab\" (300 bytes), words = [\"a\", \"aa\", …, 20 a's]", word_break(&s, &refs), false);
}
