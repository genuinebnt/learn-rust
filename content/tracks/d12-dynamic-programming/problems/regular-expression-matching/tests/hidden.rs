use solution::*;

#[test]
fn empty_vs_star() {
    check!(r#"s = "", p = "a*""#, is_match("", "a*"), true);
}

#[test]
fn empty_vs_dot() {
    check!(r#"s = "", p = ".""#, is_match("", "."), false);
}

#[test]
fn dot_star_then_more() {
    check!(r#"s = "ab", p = ".*c""#, is_match("ab", ".*c"), false);
}

#[test]
fn star_gives_one_back() {
    check!(r#"s = "aaa", p = "a*a""#, is_match("aaa", "a*a"), true);
}

#[test]
fn zero_copies_between() {
    check!(r#"s = "aaa", p = "ab*a*c*a""#, is_match("aaa", "ab*a*c*a"), true);
}

#[test]
fn trailing_star() {
    check!(r#"s = "a", p = "ab*""#, is_match("a", "ab*"), true);
}

#[test]
fn dot_star_backtracks() {
    check!(r#"s = "bbbba", p = ".*a*a""#, is_match("bbbba", ".*a*a"), true);
}

#[test]
fn pattern_too_long() {
    check!(r#"s = "a", p = ".*..a*""#, is_match("a", ".*..a*"), false);
}

#[test]
fn unicode_dot() {
    check!(r#"s = "é", p = ".""#, is_match("é", "."), true);
}

#[test]
fn unicode_star() {
    check!(r#"s = "ééé", p = "é*""#, is_match("ééé", "é*"), true);
}

#[test]
fn several_dot_stars() {
    check!(r#"s = "aasdfasdfasdfasdfas", p = "aasdf.*asdf.*asdf.*asdf.*s""#, is_match("aasdfasdfasdfasdfas", "aasdf.*asdf.*asdf.*asdf.*s"), true);
}

#[test]
fn random_vs_brute_force() {
    fn matches(s: &[char], p: &[char]) -> bool {
        if p.is_empty() {
            return s.is_empty();
        }
        let first = !s.is_empty() && (p[0] == '.' || p[0] == s[0]);
        if p.len() >= 2 && p[1] == '*' {
            matches(s, &p[2..]) || (first && matches(&s[1..], p))
        } else {
            first && matches(&s[1..], &p[1..])
        }
    }
    let mut rng = anneal_prelude::Rng::new(1253);
    let units = ["a", "b", "é", ".", "a*", "b*", ".*", "é*"];
    for _ in 0..400 {
        let n = rng.below(9);
        let s = rng.string(n, "abé");
        let k = rng.below(6);
        let p: String = (0..k).map(|_| *rng.pick(&units)).collect();
        let (sc, pc): (Vec<char>, Vec<char>) = (s.chars().collect(), p.chars().collect());
        check!(format!("s = {s:?}, p = {p:?}"), is_match(&s, &p), matches(&sc, &pc));
    }
}

#[test]
fn scale_many_stars() {
    let s = "a".repeat(40);
    let p = "a*".repeat(20) + "b";
    check!("s = 40 × 'a', p = 20 × \"a*\" then \"b\"", is_match(&s, &p), false);
}

#[test]
fn scale_long() {
    let s = "a".repeat(2000);
    let p = "a*".repeat(1000);
    check!("s = 2000 × 'a', p = 1000 × \"a*\"", is_match(&s, &p), true);
    let p = ".*".to_string() + &"a".repeat(1998) + "b";
    check!("s = 2000 × 'a', p = \".*\" + 1998 × 'a' + \"b\"", is_match(&s, &p), false);
}
