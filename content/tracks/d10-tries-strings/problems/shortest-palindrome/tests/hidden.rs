use solution::*;

#[test]
fn two_same() {
    check!(r#"s = "aa""#, shortest_palindrome("aa"), "aa");
}

#[test]
fn two_different() {
    check!(r#"s = "ab""#, shortest_palindrome("ab"), "bab");
}

#[test]
fn aab() {
    check!(r#"s = "aab""#, shortest_palindrome("aab"), "baab");
}

#[test]
fn abb() {
    check!(r#"s = "abb""#, shortest_palindrome("abb"), "bbabb");
}

#[test]
fn aabba() {
    check!(r#"s = "aabba""#, shortest_palindrome("aabba"), "abbaabba");
}

#[test]
fn emoji() {
    check!(r#"s = "🦀""#, shortest_palindrome("🦀"), "🦀");
}

#[test]
fn abac() {
    check!(r#"s = "abac""#, shortest_palindrome("abac"), "cabac");
}

#[test]
fn hash_in_the_input() {
    check!(r##"s = "#a" (a '#' separator would collide)"##, shortest_palindrome("#a"), "a#a");
}

#[test]
fn hash_run() {
    check!(r#"s = "a#a#""#, shortest_palindrome("a#a#"), "#a#a#");
}

#[test]
fn abab() {
    check!(r#"s = "abab""#, shortest_palindrome("abab"), "babab");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1024);
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "ab#é");
        let cs: Vec<char> = s.chars().collect();
        let keep = (0..=cs.len()).rev().find(|&k| cs[..k].iter().eq(cs[..k].iter().rev())).unwrap();
        let want: String = cs[keep..].iter().rev().chain(&cs).collect();
        check!(format!("s = {s:?}"), shortest_palindrome(&s), want);
    }
}

#[test]
fn scale_million() {
    // The longest palindromic prefix is the first 500000 a's; every longer prefix almost matches.
    let m = 500_000;
    let s = format!("{}b{}", "a".repeat(m), "a".repeat(m - 1));
    let got = shortest_palindrome(&s);
    let want = format!("{}b{s}", "a".repeat(m - 1));
    check!("s = 'a' × 500000 + \"b\" + 'a' × 499999", (got.len(), got == want), (want.len(), true));
}
