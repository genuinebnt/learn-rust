use solution::*;

#[test]
fn leetcode_abc() {
    check!(r#"s = "abc""#, count_substrings("abc"), 3);
}

#[test]
fn leetcode_aaa() {
    check!(r#"s = "aaa" (a, a, a, aa, aa, aaa)"#, count_substrings("aaa"), 6);
}

#[test]
fn empty() {
    check!(r#"s = """#, count_substrings(""), 0);
}

#[test]
fn single() {
    check!(r#"s = "a""#, count_substrings("a"), 1);
}

#[test]
fn even_length() {
    check!(r#"s = "abba" (a, b, b, a, bb, abba)"#, count_substrings("abba"), 6);
}

#[test]
fn characters_not_bytes() {
    check!(r#"s = "éé" (é, é, éé)"#, count_substrings("éé"), 3);
}
