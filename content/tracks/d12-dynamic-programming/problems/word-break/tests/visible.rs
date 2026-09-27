use solution::*;

#[test]
fn leetcode_leetcode() {
    check!(r#"s = "leetcode", words = ["leet", "code"]"#, word_break("leetcode", &["leet", "code"]), true);
}

#[test]
fn leetcode_reuse() {
    check!(r#"s = "applepenapple", words = ["apple", "pen"]"#, word_break("applepenapple", &["apple", "pen"]), true);
}

#[test]
fn leetcode_catsandog() {
    check!(r#"s = "catsandog", words = ["cats", "dog", "sand", "and", "cat"]"#, word_break("catsandog", &["cats", "dog", "sand", "and", "cat"]), false);
}

#[test]
fn empty_string() {
    check!(r#"s = "", words = ["a"]"#, word_break("", &["a"]), true);
}

#[test]
fn no_words() {
    check!(r#"s = "a", words = []"#, word_break("a", &[]), false);
}

#[test]
fn longest_first_fails() {
    check!(r#"s = "cars", words = ["car", "ca", "rs"]"#, word_break("cars", &["car", "ca", "rs"]), true);
}
