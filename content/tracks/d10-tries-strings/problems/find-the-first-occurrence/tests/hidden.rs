use solution::*;

#[test]
fn needle_longer() {
    check!(r#"haystack = b"ab", needle = b"abc""#, find_first(b"ab", b"abc"), None);
}

#[test]
fn equal() {
    check!(r#"haystack = b"abc", needle = b"abc""#, find_first(b"abc", b"abc"), Some(0));
}

#[test]
fn both_empty() {
    check!(r#"haystack = b"", needle = b"""#, find_first(b"", b""), Some(0));
}

#[test]
fn at_the_end() {
    check!(r#"haystack = b"xxxxy", needle = b"xy""#, find_first(b"xxxxy", b"xy"), Some(3));
}

#[test]
fn overlapping_border() {
    check!(r#"haystack = b"abababca", needle = b"ababca""#, find_first(b"abababca", b"ababca"), Some(2));
}

#[test]
fn fallback_chain() {
    check!(r#"haystack = b"aabaaabaaac", needle = b"aabaaac""#, find_first(b"aabaaabaaac", b"aabaaac"), Some(4));
}

#[test]
fn chars() {
    let h: Vec<char> = "héllo wörld".chars().collect();
    let n: Vec<char> = "wö".chars().collect();
    check!(r#"haystack = chars of "héllo wörld", needle = chars of "wö""#, find_first(&h, &n), Some(6));
}

#[test]
fn negatives() {
    check!(r#"haystack = [-1, -1, -2], needle = [-1, -2]"#, find_first(&[-1, -1, -2], &[-1, -2]), Some(1));
}

#[test]
fn strings_as_items() {
    check!(r#"haystack = ["a", "b", "a", "c"], needle = ["a", "c"]"#, find_first(&["a", "b", "a", "c"], &["a", "c"]), Some(2));
}

#[test]
fn single_miss() {
    check!(r#"haystack = b"a", needle = b"b""#, find_first(b"a", b"b"), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1012);
    for _ in 0..400 {
        let (hl, nl) = (rng.below(14), rng.below(5));
        let h: Vec<u8> = rng.vec(hl, 0, 1);
        let n: Vec<u8> = rng.vec(nl, 0, 1);
        let want = if n.is_empty() { Some(0) } else { h.windows(n.len()).position(|w| w == n.as_slice()) };
        check!(format!("haystack = {h:?}, needle = {n:?}"), find_first(&h, &n), want);
    }
}

#[test]
fn scale_million_words() {
    // A phrase search over words. Every window matches all but the needle's last word, so checking windows one by one is quadratic.
    let mut h = vec!["to"; 1_000_000];
    h.push("be");
    let mut n = vec!["to"; 100_000];
    n.push("be");
    check!("haystack = [\"to\"; 10⁶] + [\"be\"], needle = [\"to\"; 10⁵] + [\"be\"]", find_first(&h, &n), Some(900_000));
}
