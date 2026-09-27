use solution::*;

#[test]
fn leetcode_abab() {
    check!(r#"s = "abab""#, repeated_substring_pattern("abab"), true);
}

#[test]
fn leetcode_aba() {
    check!(r#"s = "aba""#, repeated_substring_pattern("aba"), false);
}

#[test]
fn leetcode_abc_four_times() {
    check!(r#"s = "abcabcabcabc""#, repeated_substring_pattern("abcabcabcabc"), true);
}

#[test]
fn single_character() {
    check!(r#"s = "a""#, repeated_substring_pattern("a"), false);
}

#[test]
fn empty() {
    check!(r#"s = """#, repeated_substring_pattern(""), false);
}

#[test]
fn must_cover_the_whole_string() {
    check!(r#"s = "abcabcab" ("abc" repeats, but doesn't fill the string)"#, repeated_substring_pattern("abcabcab"), false);
}

#[test]
fn three_copies() {
    check!(r#"s = "xyzxyzxyz""#, repeated_substring_pattern("xyzxyzxyz"), true);
}
