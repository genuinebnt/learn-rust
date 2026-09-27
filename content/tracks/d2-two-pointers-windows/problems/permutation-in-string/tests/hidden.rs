use solution::*;

#[test]
fn longer_pattern() {
    check!(r#"pattern = "abc", s = "ab""#, check_inclusion("abc", "ab"), false);
}

#[test]
fn whole_string() {
    check!(r#"pattern = "adc", s = "dcda""#, check_inclusion("adc", "dcda"), true);
}

#[test]
fn single_match() {
    check!(r#"pattern = "a", s = "a""#, check_inclusion("a", "a"), true);
}

#[test]
fn single_miss() {
    check!(r#"pattern = "a", s = "b""#, check_inclusion("a", "b"), false);
}

#[test]
fn counts_matter() {
    check!(r#"pattern = "aab", s = "abbab""#, check_inclusion("aab", "abbab"), false);
}

#[test]
fn repeated_letters() {
    check!(r#"pattern = "aab", s = "xabab""#, check_inclusion("aab", "xabab"), true);
}

#[test]
fn at_the_end() {
    check!(r#"pattern = "xyz", s = "aaaaazyx""#, check_inclusion("xyz", "aaaaazyx"), true);
}

#[test]
fn same_length_not_perm() {
    check!(r#"pattern = "abc", s = "abd""#, check_inclusion("abc", "abd"), false);
}

#[test]
fn split_across_gap() {
    check!(r#"pattern = "ab", s = "acb""#, check_inclusion("ab", "acb"), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(214);
    for _ in 0..400 {
        let pn = 1 + rng.below(4);
        let n = 1 + rng.below(10);
        let pattern = rng.string(pn, "abc");
        let s = rng.string(n, "abc");
        let mut want_sorted: Vec<u8> = pattern.bytes().collect();
        want_sorted.sort();
        let want = s.as_bytes().windows(pn).any(|w| {
            let mut w = w.to_vec();
            w.sort();
            w == want_sorted
        });
        check!(format!("pattern = {pattern:?}, s = {s:?}"), check_inclusion(&pattern, &s), want);
    }
}

#[test]
fn scale_200k() {
    let pattern = "a".repeat(99_999) + "b";
    let s = "a".repeat(199_999) + "b";
    let t = "a".repeat(200_000);
    check!("pattern = \"a\" × 99999 + \"b\", s = \"a\" × 199999 + \"b\" / \"a\" × 200000", (check_inclusion(&pattern, &s), check_inclusion(&pattern, &t)), (true, false));
}
