use solution::*;

#[test]
fn empty() {
    check!(r#""", banned = []"#, most_common_word("", &[]), "");
}

#[test]
fn punctuation_only() {
    check!(r#""!!! ,, .", banned = []"#, most_common_word("!!! ,, .", &[]), "");
}

#[test]
fn digits_split_words() {
    check!(r#""abc1abc2def", banned = []"#, most_common_word("abc1abc2def", &[]), "abc");
}

#[test]
fn apostrophe_splits() {
    check!(r#""don't don't stop", banned = []"#, most_common_word("don't don't stop", &[]), "don");
}

#[test]
fn banned_matches_any_case() {
    check!(r#""HIT hit ball", banned = ["hit"]"#, most_common_word("HIT hit ball", &["hit"]), "ball");
}

#[test]
fn non_ascii_splits() {
    check!(r#""naïve naïve x", banned = []"#, most_common_word("naïve naïve x", &[]), "na");
}

#[test]
fn commas_without_spaces() {
    check!(r#""a, a, a, a, b,b,b,c, c", banned = ["a"]"#, most_common_word("a, a, a, a, b,b,b,c, c", &["a"]), "b");
}

#[test]
fn banned_absent() {
    check!(r#""x x y", banned = ["zzz"]"#, most_common_word("x x y", &["zzz"]), "x");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4001);
    let bans = ["", "a", "b"];
    for _ in 0..300 {
        let len = rng.below(14);
        let text = rng.string(len, "abAB .,1");
        let ban = *rng.pick(&bans);
        let banned: Vec<&str> = if ban.is_empty() { vec![] } else { vec![ban] };
        let words: Vec<String> = text.split(|c: char| !c.is_ascii_alphabetic()).filter(|w| !w.is_empty()).map(|w| w.to_ascii_lowercase()).filter(|w| !banned.contains(&w.as_str())).collect();
        let mut want = String::new();
        let mut best = 0;
        for w in &words {
            let c = words.iter().filter(|x| *x == w).count();
            if c > best || (c == best && *w < want) {
                best = c;
                want = w.clone();
            }
        }
        check!(format!("paragraph = {text:?}, banned = {banned:?}"), most_common_word(&text, &banned), want);
    }
}

#[test]
fn scale_200k_words() {
    fn word(mut i: usize) -> String {
        let mut w = String::new();
        for _ in 0..4 {
            w.push(char::from(b'a' + (i % 26) as u8));
            i /= 26;
        }
        w
    }
    let mut text = String::new();
    for i in 0..200_000 {
        text.push_str(&word(i % 100_000));
        text.push(' ');
    }
    text.push_str(&word(77_777));
    check!("200000 words, 100000 distinct, one of them once more", most_common_word(&text, &[]), word(77_777));
}
