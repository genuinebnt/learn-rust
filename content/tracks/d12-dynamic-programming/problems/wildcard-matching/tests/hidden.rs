use solution::*;

#[test]
fn question_needs_a_char() {
    check!(r#"s = "", p = "?""#, is_match("", "?"), false);
}

#[test]
fn empty_pattern() {
    check!(r#"s = "a", p = """#, is_match("a", ""), false);
}

#[test]
fn leetcode_no_match() {
    check!(r#"s = "acdcb", p = "a*c?b""#, is_match("acdcb", "a*c?b"), false);
}

#[test]
fn unicode_question() {
    check!(r#"s = "héllo", p = "h?llo""#, is_match("héllo", "h?llo"), true);
}

#[test]
fn emoji_each_one_char() {
    check!(r#"s = "🦀🦀", p = "??""#, is_match("🦀🦀", "??"), true);
}

#[test]
fn emoji_too_short() {
    check!(r#"s = "🦀", p = "??""#, is_match("🦀", "??"), false);
}

#[test]
fn many_stars() {
    check!(r#"s = "aaaa", p = "***a""#, is_match("aaaa", "***a"), true);
}

#[test]
fn stars_and_questions() {
    check!(r#"s = "abcabczzzde", p = "*abc???de*""#, is_match("abcabczzzde", "*abc???de*"), true);
}

#[test]
fn mississippi() {
    check!(r#"s = "mississippi", p = "m??*ss*?i*pi""#, is_match("mississippi", "m??*ss*?i*pi"), false);
}

#[test]
fn one_question_too_many() {
    check!(r#"s = "ab", p = "*?*?*?""#, is_match("ab", "*?*?*?"), false);
}

#[test]
fn random_vs_brute_force() {
    fn matches(s: &[char], p: &[char]) -> bool {
        match p.split_first() {
            None => s.is_empty(),
            Some(('*', rest)) => (0..=s.len()).any(|k| matches(&s[k..], rest)),
            Some((&q, rest)) => !s.is_empty() && (q == '?' || q == s[0]) && matches(&s[1..], rest),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1252);
    for _ in 0..400 {
        let (n, m) = (rng.below(9), rng.below(7));
        let s = rng.string(n, "abé");
        let p = rng.string(m, "ab?*é");
        let (sc, pc): (Vec<char>, Vec<char>) = (s.chars().collect(), p.chars().collect());
        check!(format!("s = {s:?}, p = {p:?}"), is_match(&s, &p), matches(&sc, &pc));
    }
}

#[test]
fn scale_many_stars() {
    let s = "a".repeat(3000);
    let p = "*a".repeat(12) + "b";
    check!("s = 3000 × 'a', p = 12 × \"*a\" then \"b\"", is_match(&s, &p), false);
}

#[test]
fn scale_long_pattern() {
    let s = "a".repeat(4000);
    let p = "*".to_string() + &"a".repeat(2000) + "*b";
    check!("s = 4000 × 'a', p = '*' + 2000 × 'a' + \"*b\"", is_match(&s, &p), false);
    let p = "*".to_string() + &"?".repeat(1999) + "*a";
    check!("s = 4000 × 'a', p = '*' + 1999 × '?' + \"*a\"", is_match(&s, &p), true);
}
