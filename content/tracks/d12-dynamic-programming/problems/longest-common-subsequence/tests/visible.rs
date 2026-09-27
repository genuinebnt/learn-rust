use solution::*;

#[test]
fn leetcode_ace() {
    check!(r#"a = "abcde", b = "ace""#, longest_common_subsequence("abcde", "ace"), 3);
}

#[test]
fn leetcode_same() {
    check!(r#"a = "abc", b = "abc""#, longest_common_subsequence("abc", "abc"), 3);
}

#[test]
fn leetcode_nothing_shared() {
    check!(r#"a = "abc", b = "def""#, longest_common_subsequence("abc", "def"), 0);
}

#[test]
fn empty() {
    check!(r#"a = "", b = "abc""#, longest_common_subsequence("", "abc"), 0);
}

#[test]
fn order_matters() {
    check!(r#"a = "abc", b = "cba""#, longest_common_subsequence("abc", "cba"), 1);
}

#[test]
fn gaps_allowed() {
    check!(r#"a = "abcxdef", b = "abcydef""#, longest_common_subsequence("abcxdef", "abcydef"), 6);
}
