use solution::*;

#[test]
fn two_to_one() {
    check!(r#"s = "ab", t = "aa""#, is_isomorphic("ab", "aa"), false);
}

#[test]
fn badc_baba() {
    check!(r#"s = "badc", t = "baba""#, is_isomorphic("badc", "baba"), false);
}

#[test]
fn empty() {
    check!(r#"s = "", t = """#, is_isomorphic("", ""), true);
}

#[test]
fn single() {
    check!(r#"s = "a", t = "z""#, is_isomorphic("a", "z"), true);
}

#[test]
fn swap() {
    check!(r#"s = "ab", t = "ba""#, is_isomorphic("ab", "ba"), true);
}

#[test]
fn one_to_two() {
    check!(r#"s = "aa", t = "ab""#, is_isomorphic("aa", "ab"), false);
}

#[test]
fn identity() {
    check!(r#"s = "abc", t = "abc""#, is_isomorphic("abc", "abc"), true);
}

#[test]
fn digits_and_symbols() {
    check!(r#"s = "1#1", t = "a!a""#, is_isomorphic("1#1", "a!a"), true);
}

#[test]
fn space_and_upper() {
    check!(r#"s = "A b", t = "xyx""#, is_isomorphic("A b", "xyx"), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(9);
    for _ in 0..400 {
        let n = rng.below(8);
        let s = rng.string(n, "abc");
        let t = rng.string(n, "xyz");
        let (a, b) = (s.as_bytes(), t.as_bytes());
        let want = (0..n).all(|i| (0..n).all(|j| (a[i] == a[j]) == (b[i] == b[j])));
        check!(format!("s = {s:?}, t = {t:?}"), is_isomorphic(&s, &t), want);
    }
}

#[test]
fn scale_200k() {
    let s: String = (0..200_000).map(|i| (b'!' + (i % 90) as u8) as char).collect();
    let t: String = s.bytes().map(|b| (b'!' + (b - b'!' + 1) % 90) as char).collect();
    check!("s and t = 200000 chars, t shifts each of 90 symbols by one", is_isomorphic(&s, &t), true);
}
