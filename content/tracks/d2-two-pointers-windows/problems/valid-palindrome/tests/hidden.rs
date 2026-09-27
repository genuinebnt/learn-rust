use solution::*;

#[test]
fn digits_matter() {
    check!(r#"s = "0P""#, is_palindrome("0P"), false);
}

#[test]
fn empty() {
    check!(r#"s = """#, is_palindrome(""), true);
}

#[test]
fn single() {
    check!(r#"s = "a""#, is_palindrome("a"), true);
}

#[test]
fn mixed_case() {
    check!(r#"s = "Aa""#, is_palindrome("Aa"), true);
}

#[test]
fn two_different() {
    check!(r#"s = "ab""#, is_palindrome("ab"), false);
}

#[test]
fn digits() {
    check!(r#"s = "12321""#, is_palindrome("12321"), true);
}

#[test]
fn digit_mismatch() {
    check!(r#"s = "1a2""#, is_palindrome("1a2"), false);
}

#[test]
fn non_ascii_skipped() {
    check!(r#"s = "éa""#, is_palindrome("éa"), true);
}

#[test]
fn non_ascii_between() {
    check!(r#"s = "ab😀 ÜBA""#, is_palindrome("ab😀 ÜBA"), true);
}

#[test]
fn punctuation_both_ends() {
    check!(r#"s = ".,a,.b""#, is_palindrome(".,a,.b"), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(201);
    for _ in 0..400 {
        let n = rng.below(10);
        let s = rng.string(n, "aAbB01 ,.é");
        let kept: Vec<char> = s.chars().filter(|c| c.is_ascii_alphanumeric()).map(|c| c.to_ascii_lowercase()).collect();
        let want = kept.iter().eq(kept.iter().rev());
        check!(format!("s = {s:?}"), is_palindrome(&s), want);
    }
}

#[test]
fn scale_200k() {
    let half: String = (0..100_000).map(|i| if i % 3 == 1 { ',' } else { (b'a' + (i % 26) as u8) as char }).collect();
    let s: String = half.chars().chain(half.chars().rev().map(|c| c.to_ascii_uppercase())).collect();
    let mut t = s.clone();
    t.pop();
    t.push('!');
    check!("s = a 200000-byte palindrome with punctuation, and the same with its last letter changed", (is_palindrome(&s), is_palindrome(&t)), (true, false));
}
