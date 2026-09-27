use solution::*;

#[test]
fn leetcode_too_short() {
    check!(r#"s = "aa", p = "a""#, is_match("aa", "a"), false);
}

#[test]
fn leetcode_star() {
    check!(r#"s = "aa", p = "*""#, is_match("aa", "*"), true);
}

#[test]
fn leetcode_question() {
    check!(r#"s = "cb", p = "?a""#, is_match("cb", "?a"), false);
}

#[test]
fn both_empty() {
    check!(r#"s = "", p = """#, is_match("", ""), true);
}

#[test]
fn star_matches_nothing() {
    check!(r#"s = "", p = "*""#, is_match("", "*"), true);
}

#[test]
fn two_stars() {
    check!(r#"s = "adceb", p = "*a*b""#, is_match("adceb", "*a*b"), true);
}
