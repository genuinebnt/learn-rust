use solution::*;

#[test]
fn abc() {
    check!(r#"s = "abcabcbb""#, length_of_longest_substring("abcabcbb"), 3);
}

#[test]
fn all_same() {
    check!(r#"s = "bbbbb""#, length_of_longest_substring("bbbbb"), 1);
}

#[test]
fn pwwkew() {
    check!(r#"s = "pwwkew""#, length_of_longest_substring("pwwkew"), 3);
}
