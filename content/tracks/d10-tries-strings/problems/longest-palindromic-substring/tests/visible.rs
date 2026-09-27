use solution::*;

#[test]
fn leetcode_babad() {
    check!(r#"s = "babad" ("aba" is as long, but "bab" starts first)"#, longest_palindrome("babad"), "bab");
}

#[test]
fn leetcode_cbbd() {
    check!(r#"s = "cbbd""#, longest_palindrome("cbbd"), "bb");
}

#[test]
fn single() {
    check!(r#"s = "a""#, longest_palindrome("a"), "a");
}

#[test]
fn empty() {
    check!(r#"s = """#, longest_palindrome(""), "");
}

#[test]
fn no_repeat_takes_the_first_letter() {
    check!(r#"s = "ac""#, longest_palindrome("ac"), "a");
}

#[test]
fn unicode() {
    check!(r#"s = "ñoño""#, longest_palindrome("ñoño"), "ñoñ");
}
