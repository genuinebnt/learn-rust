use solution::*;

#[test]
fn leetcode_bbbab() {
    check!(r#"s = "bbbab""#, longest_palindrome_subseq("bbbab"), 4);
}

#[test]
fn leetcode_cbbd() {
    check!(r#"s = "cbbd""#, longest_palindrome_subseq("cbbd"), 2);
}

#[test]
fn empty() {
    check!(r#"s = """#, longest_palindrome_subseq(""), 0);
}

#[test]
fn single() {
    check!(r#"s = "a""#, longest_palindrome_subseq("a"), 1);
}

#[test]
fn all_different() {
    check!(r#"s = "abcde""#, longest_palindrome_subseq("abcde"), 1);
}

#[test]
fn gaps_allowed() {
    check!(r#"s = "aebcbda" ("abcba")"#, longest_palindrome_subseq("aebcbda"), 5);
}
