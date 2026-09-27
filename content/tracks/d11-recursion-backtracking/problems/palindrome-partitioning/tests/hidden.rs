use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn four_equal() {
    check!(r#"s = "aaaa""#, sorted(partition("aaaa")), vec![vec!["a", "a", "a", "a"], vec!["a", "a", "aa"], vec!["a", "aa", "a"], vec!["a", "aaa"], vec!["aa", "a", "a"], vec!["aa", "aa"], vec!["aaa", "a"], vec!["aaaa"]]);
}

#[test]
fn even_palindrome() {
    check!(r#"s = "abba""#, sorted(partition("abba")), vec![vec!["a", "b", "b", "a"], vec!["a", "bb", "a"], vec!["abba"]]);
}

#[test]
fn nested_palindromes() {
    check!(r#"s = "racecar""#, sorted(partition("racecar")), vec![vec!["r", "a", "c", "e", "c", "a", "r"], vec!["r", "a", "cec", "a", "r"], vec!["r", "aceca", "r"], vec!["racecar"]]);
}

#[test]
fn two_different() {
    check!(r#"s = "ab""#, partition("ab"), vec![vec!["a", "b"]]);
}

#[test]
fn ends_match_but_not_a_palindrome() {
    check!(r#"s = "abca""#, partition("abca"), vec![vec!["a", "b", "c", "a"]]);
}

#[test]
fn sixteen_distinct() {
    check!(r#"s = "abcdefghijklmnop""#, partition("abcdefghijklmnop").len(), 1);
}

#[test]
fn pieces_rebuild_s() {
    check!(r#"s = "aabbaab", every split joins back to s"#, partition("aabbaab").iter().all(|p| p.concat() == "aabbaab"), true);
}

#[test]
fn abcba() {
    check!(r#"s = "abcba""#, sorted(partition("abcba")), vec![vec!["a", "b", "c", "b", "a"], vec!["a", "bcb", "a"], vec!["abcba"]]);
}

#[test]
fn random_vs_every_cut_set() {
    let mut rng = anneal_prelude::Rng::new(1130);
    for _ in 0..300 {
        let n = rng.int(1, 10) as usize;
        let alphabet = *rng.pick(&["ab", "abc", "a"]);
        let s = rng.string(n, alphabet);
        // Each bit of `cuts` says whether s is cut after that position.
        let mut want: Vec<Vec<&str>> = Vec::new();
        for cuts in 0u32..1 << (n - 1) {
            let (mut pieces, mut start) = (Vec::new(), 0);
            for i in 0..n {
                if i == n - 1 || cuts >> i & 1 == 1 {
                    pieces.push(&s[start..=i]);
                    start = i + 1;
                }
            }
            if pieces.iter().all(|p| p.bytes().eq(p.bytes().rev())) {
                want.push(pieces);
            }
        }
        want.sort();
        check!(format!("s = {s:?}"), sorted(partition(&s)), want);
    }
}

#[test]
fn scale_sixteen_equal() {
    let s = "a".repeat(16);
    let got = partition(&s);
    check!("s = 16 × \"a\"", (got.len(), got.iter().all(|p| p.concat() == s)), (32_768, true));
}
