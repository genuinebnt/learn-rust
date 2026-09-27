use solution::*;

#[test]
fn leetcode_too_short() {
    check!(r#"s = "aa", p = "a""#, is_match("aa", "a"), false);
}

#[test]
fn leetcode_star_repeats() {
    check!(r#"s = "aa", p = "a*""#, is_match("aa", "a*"), true);
}

#[test]
fn leetcode_dot_star() {
    check!(r#"s = "ab", p = ".*""#, is_match("ab", ".*"), true);
}

#[test]
fn star_can_match_nothing() {
    check!(r#"s = "aab", p = "c*a*b""#, is_match("aab", "c*a*b"), true);
}

#[test]
fn mississippi() {
    check!(r#"s = "mississippi", p = "mis*is*p*.""#, is_match("mississippi", "mis*is*p*."), false);
}

#[test]
fn both_empty() {
    check!(r#"s = "", p = """#, is_match("", ""), true);
}
