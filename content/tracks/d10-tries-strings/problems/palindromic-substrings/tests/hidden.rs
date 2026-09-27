use solution::*;

#[test]
fn four_same() {
    check!(r#"s = "aaaa""#, count_substrings("aaaa"), 10);
}

#[test]
fn odd_nested() {
    check!(r#"s = "abcba""#, count_substrings("abcba"), 7);
}

#[test]
fn alternating() {
    check!(r#"s = "abab""#, count_substrings("abab"), 6);
}

#[test]
fn racecar() {
    check!(r#"s = "racecar""#, count_substrings("racecar"), 10);
}

#[test]
fn emoji() {
    check!(r#"s = "🦀🦀""#, count_substrings("🦀🦀"), 3);
}

#[test]
fn case_sensitive() {
    check!(r#"s = "Aa""#, count_substrings("Aa"), 2);
}

#[test]
fn palindrome_then_noise() {
    check!(r#"s = "abcdcbaxyz""#, count_substrings("abcdcbaxyz"), 13);
}

#[test]
fn two_different() {
    check!(r#"s = "ab""#, count_substrings("ab"), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1015);
    for _ in 0..400 {
        let len = rng.below(12);
        let s = rng.string(len, "abé");
        let cs: Vec<char> = s.chars().collect();
        let mut want = 0;
        for i in 0..cs.len() {
            for j in i + 1..=cs.len() {
                let w = &cs[i..j];
                want += w.iter().eq(w.iter().rev()) as usize;
            }
        }
        check!(format!("s = {s:?}"), count_substrings(&s), want);
    }
}

#[test]
fn scale_5000_same_letter() {
    let s = "a".repeat(5000);
    check!("s = 'a' × 5000", count_substrings(&s), 5000 * 5001 / 2);
}
