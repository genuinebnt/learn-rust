use solution::*;

#[test]
fn empty() {
    check!(r#"s = """#, length_of_longest_substring(""), 0);
}

#[test]
fn stale_repeat() {
    check!(r#"s = "abba""#, length_of_longest_substring("abba"), 2);
}

#[test]
fn spaces() {
    check!(r#"s = " a b""#, length_of_longest_substring(" a b"), 3);
}
