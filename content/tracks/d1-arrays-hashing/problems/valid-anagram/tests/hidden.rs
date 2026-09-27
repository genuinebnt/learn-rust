use solution::*;

#[test]
fn empty() {
    check!(r#"s = "", t = """#, is_anagram("", ""), true);
}

#[test]
fn same_letters_different_counts() {
    check!(r#"s = "aab", t = "abb""#, is_anagram("aab", "abb"), false);
}

#[test]
fn shorter_first() {
    check!(r#"s = "a", t = "ab""#, is_anagram("a", "ab"), false);
}

#[test]
fn one_empty() {
    check!(r#"s = "", t = "a""#, is_anagram("", "a"), false);
}

#[test]
fn single_same() {
    check!(r#"s = "z", t = "z""#, is_anagram("z", "z"), true);
}

#[test]
fn single_different() {
    check!(r#"s = "a", t = "b""#, is_anagram("a", "b"), false);
}

#[test]
fn identical() {
    check!(r#"s = "listen", t = "listen""#, is_anagram("listen", "listen"), true);
}

#[test]
fn whole_alphabet() {
    check!(r#"s = "abc…z", t = "zyx…a""#, is_anagram("abcdefghijklmnopqrstuvwxyz", "zyxwvutsrqponmlkjihgfedcba"), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(5);
    for _ in 0..300 {
        let n = rng.below(8);
        let s = rng.string(n, "abc");
        let t = if rng.bool() {
            let mut cs: Vec<char> = s.chars().collect();
            rng.shuffle(&mut cs);
            cs.into_iter().collect()
        } else {
            let m = rng.below(8);
            rng.string(m, "abc")
        };
        let sorted = |x: &str| { let mut v: Vec<char> = x.chars().collect(); v.sort(); v };
        check!(format!("s = {s:?}, t = {t:?}"), is_anagram(&s, &t), sorted(&s) == sorted(&t));
    }
}

#[test]
fn scale_200k() {
    let s = "a".repeat(100_000) + &"b".repeat(100_000);
    let t = "b".repeat(100_000) + &"a".repeat(100_000);
    check!("s = a × 100000 then b × 100000, t = the reverse", is_anagram(&s, &t), true);
}
