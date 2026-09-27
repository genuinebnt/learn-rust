use solution::*;

#[test]
fn leetcode_sea_eat() {
    check!(r#"a = "sea", b = "eat""#, min_distance("sea", "eat"), 2);
}

#[test]
fn leetcode_leetcode() {
    check!(r#"a = "leetcode", b = "etco""#, min_distance("leetcode", "etco"), 4);
}

#[test]
fn empty() {
    check!(r#"a = "", b = "abc""#, min_distance("", "abc"), 3);
}

#[test]
fn already_equal() {
    check!(r#"a = "abc", b = "abc""#, min_distance("abc", "abc"), 0);
}

#[test]
fn no_replacing() {
    check!(r#"a = "a", b = "b" (delete both)"#, min_distance("a", "b"), 2);
}
