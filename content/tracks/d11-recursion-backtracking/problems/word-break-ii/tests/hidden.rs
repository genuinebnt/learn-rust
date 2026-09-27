use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn single_letter() {
    check!(r#"s = "a", word_dict = ["a"]"#, word_break("a", &["a"]), vec!["a"]);
}

#[test]
fn no_word_fits() {
    check!(r#"s = "b", word_dict = ["a"]"#, word_break("b", &["a"]), Vec::<String>::new());
}

#[test]
fn word_longer_than_s() {
    check!(r#"s = "ab", word_dict = ["abc"]"#, word_break("ab", &["abc"]), Vec::<String>::new());
}

#[test]
fn four_as() {
    check!(r#"s = "aaaa", word_dict = ["a", "aa"]"#, sorted(word_break("aaaa", &["a", "aa"])), vec!["a a a a", "a a aa", "a aa a", "aa a a", "aa aa"]);
}

#[test]
fn leetcode_seven_as() {
    check!(r#"s = "aaaaaaa", word_dict = ["aaaa", "aa", "a"]"#, word_break("aaaaaaa", &["aaaa", "aa", "a"]).len(), 31);
}

#[test]
fn prefix_trap() {
    check!(r#"s = "catsdog", word_dict = ["cat", "cats", "sdog", "dog"]"#, sorted(word_break("catsdog", &["cat", "cats", "sdog", "dog"])), vec!["cat sdog", "cats dog"]);
}

#[test]
fn last_letter_unmatched() {
    check!(r#"s = "aaab", word_dict = ["a", "aa", "aaa"]"#, word_break("aaab", &["a", "aa", "aaa"]), Vec::<String>::new());
}

#[test]
fn hundred_letters() {
    check!(r#"s = "catsanddog" × 10, word_dict = ["cat", "cats", "and", "sand", "dog"]: 2¹⁰ sentences"#, { let s = "catsanddog".repeat(10); let all = word_break(&s, &["cat", "cats", "and", "sand", "dog"]); (all.len(), all.iter().all(|x| x.replace(' ', "") == s)) }, (1024, true));
}

/// Every way to cut `s` into pieces, kept when every piece is a word.
fn brute(s: &str, dict: &[&str]) -> Vec<String> {
    let n = s.len();
    let mut out = Vec::new();
    for cuts in 0..1u32 << (n - 1) {
        let mut pieces = Vec::new();
        let mut start = 0;
        for i in 1..=n {
            if i == n || cuts >> (i - 1) & 1 == 1 {
                pieces.push(&s[start..i]);
                start = i;
            }
        }
        if pieces.iter().all(|p| dict.contains(p)) {
            out.push(pieces.join(" "));
        }
    }
    out
}

#[test]
fn random_vs_every_cut() {
    let mut rng = anneal_prelude::Rng::new(1136);
    for _ in 0..300 {
        let len = rng.int(1, 10) as usize;
        let s = rng.string(len, "ab");
        let count = rng.int(1, 5) as usize;
        let mut words = Vec::new();
        for _ in 0..count {
            let wlen = rng.int(1, 3) as usize;
            words.push(rng.string(wlen, "ab"));
        }
        let dict: Vec<&str> = words.iter().map(String::as_str).collect();
        check!(format!("s = {s:?}, word_dict = {dict:?}"), sorted(word_break(&s, &dict)), sorted(brute(&s, &dict)));
    }
}

#[test]
fn many_sentences() {
    // Fibonacci(21) ways to write 20 as a sum of 1s and 2s.
    let s = "a".repeat(20);
    let mut all = word_break(&s, &["a", "aa"]);
    all.sort();
    all.dedup();
    check!("s = 20 × \"a\", word_dict = [\"a\", \"aa\"]: distinct sentences", all.len(), 10946);
}

#[test]
fn scale_no_sentence() {
    let s = "a".repeat(60) + "b";
    check!("s = 60 × \"a\" + \"b\", word_dict = [\"a\", \"aa\", \"aaa\", \"aaaa\", \"aaaaa\"]",
        word_break(&s, &["a", "aa", "aaa", "aaaa", "aaaaa"]), Vec::<String>::new());
}

#[test]
fn scale_one_long_word() {
    // Only the 37-letter word covers the b; every split of the a's before it is a dead end.
    let s = "a".repeat(36) + "b";
    check!("s = 36 × \"a\" + \"b\", word_dict = [\"a\", \"aa\", \"aaa\", \"aaaa\", s]",
        word_break(&s, &["a", "aa", "aaa", "aaaa", s.as_str()]), vec![s.clone()]);
}
