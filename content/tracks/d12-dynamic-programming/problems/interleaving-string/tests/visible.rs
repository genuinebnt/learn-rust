use solution::*;

#[test]
fn leetcode_true() {
    check!(r#"s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac""#, is_interleave("aabcc", "dbbca", "aadbbcbcac"), true);
}

#[test]
fn leetcode_false() {
    check!(r#"s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc""#, is_interleave("aabcc", "dbbca", "aadbbbaccc"), false);
}

#[test]
fn leetcode_all_empty() {
    check!(r#"s1 = "", s2 = "", s3 = """#, is_interleave("", "", ""), true);
}

#[test]
fn one_side_empty() {
    check!(r#"s1 = "a", s2 = "", s3 = "a""#, is_interleave("a", "", "a"), true);
}

#[test]
fn length_mismatch() {
    check!(r#"s1 = "a", s2 = "b", s3 = "abc""#, is_interleave("a", "b", "abc"), false);
}

#[test]
fn either_string_first() {
    check!(r#"s1 = "a", s2 = "b", s3 = "ba""#, is_interleave("a", "b", "ba"), true);
}
