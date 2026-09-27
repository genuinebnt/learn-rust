use solution::*;

#[test]
fn none() {
    check!(r#"s = "aaaa", p = "b""#, find_anagrams("aaaa", "b"), Vec::<usize>::new());
}

#[test]
fn longer_pattern() {
    check!(r#"s = "a", p = "ab""#, find_anagrams("a", "ab"), Vec::<usize>::new());
}

#[test]
fn empty_pattern() {
    check!(r#"s = "abc", p = """#, find_anagrams("abc", ""), Vec::<usize>::new());
}

#[test]
fn empty_s() {
    check!(r#"s = "", p = "a""#, find_anagrams("", "a"), Vec::<usize>::new());
}

#[test]
fn whole_string() {
    check!(r#"s = "bca", p = "abc""#, find_anagrams("bca", "abc"), vec![0]);
}

#[test]
fn single_letters() {
    check!(r#"s = "aaa", p = "a""#, find_anagrams("aaa", "a"), vec![0, 1, 2]);
}

#[test]
fn counts_matter() {
    check!(r#"s = "abbab", p = "aab""#, find_anagrams("abbab", "aab"), Vec::<usize>::new());
}

#[test]
fn last_window() {
    check!(r#"s = "xxxba", p = "ab""#, find_anagrams("xxxba", "ab"), vec![3]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(215);
    for _ in 0..400 {
        let pn = 1 + rng.below(4);
        let n = rng.below(11);
        let p = rng.string(pn, "abc");
        let s = rng.string(n, "abc");
        let mut key: Vec<u8> = p.bytes().collect();
        key.sort();
        let want: Vec<usize> = (0..(n + 1).saturating_sub(pn))
            .filter(|&i| {
                let mut w = s.as_bytes()[i..i + pn].to_vec();
                w.sort();
                w == key
            })
            .collect();
        check!(format!("s = {s:?}, p = {p:?}"), find_anagrams(&s, &p), want);
    }
}

#[test]
fn scale_200k() {
    let s = "a".repeat(199_999) + "b";
    let p = "a".repeat(99_999) + "b";
    check!("s = \"a\" × 199999 + \"b\", p = \"a\" × 99999 + \"b\"", find_anagrams(&s, &p), vec![100_000]);
}
