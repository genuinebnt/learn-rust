use solution::*;

#[test]
fn duplicates_needed() {
    check!(r#"s = "aaflslflsldkalskaaa", t = "aaa""#, min_window("aaflslflsldkalskaaa", "aaa"), "aaa");
}

#[test]
fn leftmost_tie() {
    check!(r#"s = "abcab", t = "ab""#, min_window("abcab", "ab"), "ab");
}
