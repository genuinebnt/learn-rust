use solution::*;

#[test]
fn two_same_letters() {
    check!(r#"s = "zz""#, repeated_substring_pattern("zz"), true);
}

#[test]
fn two_different_letters() {
    check!(r#"s = "ab""#, repeated_substring_pattern("ab"), false);
}

#[test]
fn border_but_no_period() {
    check!(r#"s = "abaab""#, repeated_substring_pattern("abaab"), false);
}

#[test]
fn unit_with_inner_repeat() {
    check!(r#"s = "abaababaab" ("abaab" twice)"#, repeated_substring_pattern("abaababaab"), true);
}

#[test]
fn almost() {
    check!(r#"s = "abcabcabd""#, repeated_substring_pattern("abcabcabd"), false);
}

#[test]
fn accented() {
    check!(r#"s = "éaéa""#, repeated_substring_pattern("éaéa"), true);
}

#[test]
fn cjk() {
    check!(r#"s = "日本日本日本""#, repeated_substring_pattern("日本日本日本"), true);
}

#[test]
fn single_multibyte_char() {
    check!(r#"s = "é" (2 bytes, 1 character)"#, repeated_substring_pattern("é"), false);
}

#[test]
fn same_letter_many_times() {
    check!(r#"s = 'q' × 7"#, repeated_substring_pattern(&"q".repeat(7)), true);
}

#[test]
fn prime_length_mixed() {
    check!(r#"s = "aabaa""#, repeated_substring_pattern("aabaa"), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1013);
    for _ in 0..400 {
        let s = if rng.bool() {
            let (ul, k) = (1 + rng.below(3), 1 + rng.below(4));
            rng.string(ul, "ab").repeat(k)
        } else {
            let len = rng.below(10);
            rng.string(len, "ab")
        };
        let n = s.len();
        let want = (1..n).any(|p| n % p == 0 && s[..p].repeat(n / p) == s);
        check!(format!("s = {s:?}"), repeated_substring_pattern(&s), want);
    }
}

#[test]
fn scale_200k() {
    // Every candidate period matches until the very last byte.
    let no = format!("{}b", "a".repeat(199_999));
    let yes = format!("{}b", "a".repeat(99_999)).repeat(2);
    check!("s = 'a' × 199999 + \"b\"; s = ('a' × 99999 + \"b\") × 2", (repeated_substring_pattern(&no), repeated_substring_pattern(&yes)), (false, true));
}
