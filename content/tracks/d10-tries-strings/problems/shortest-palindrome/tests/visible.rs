use solution::*;

#[test]
fn leetcode_aacecaaa() {
    check!(r#"s = "aacecaaa""#, shortest_palindrome("aacecaaa"), "aaacecaaa");
}

#[test]
fn leetcode_abcd() {
    check!(r#"s = "abcd""#, shortest_palindrome("abcd"), "dcbabcd");
}

#[test]
fn empty() {
    check!(r#"s = """#, shortest_palindrome(""), "");
}

#[test]
fn single() {
    check!(r#"s = "a""#, shortest_palindrome("a"), "a");
}

#[test]
fn already_a_palindrome() {
    check!(r#"s = "aba""#, shortest_palindrome("aba"), "aba");
}

#[test]
fn unicode() {
    check!(r#"s = "éa""#, shortest_palindrome("éa"), "aéa");
}
