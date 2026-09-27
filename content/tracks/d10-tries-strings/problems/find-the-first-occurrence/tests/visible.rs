use solution::*;

#[test]
fn leetcode_sadbutsad() {
    check!(r#"haystack = b"sadbutsad", needle = b"sad""#, find_first(b"sadbutsad", b"sad"), Some(0));
}

#[test]
fn leetcode_leeto() {
    check!(r#"haystack = b"leetcode", needle = b"leeto""#, find_first(b"leetcode", b"leeto"), None);
}

#[test]
fn empty_needle() {
    check!(r#"haystack = b"abc", needle = b"""#, find_first(b"abc", b""), Some(0));
}

#[test]
fn empty_haystack() {
    check!(r#"haystack = b"", needle = b"a""#, find_first(b"", b"a"), None);
}

#[test]
fn first_of_several() {
    check!(r#"haystack = b"abcabc", needle = b"bc""#, find_first(b"abcabc", b"bc"), Some(1));
}

#[test]
fn mismatch_must_not_skip_a_start() {
    check!(r#"haystack = b"aaab", needle = b"aab" (the match starts inside the failed attempt)"#, find_first(b"aaab", b"aab"), Some(1));
}

#[test]
fn numbers() {
    check!(r#"haystack = [1, 2, 1, 2, 3], needle = [1, 2, 3]"#, find_first(&[1, 2, 1, 2, 3], &[1, 2, 3]), Some(2));
}
