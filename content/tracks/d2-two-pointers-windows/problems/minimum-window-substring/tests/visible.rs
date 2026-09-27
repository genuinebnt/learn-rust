use solution::*;

#[test]
fn classic() {
    check!(r#"s = "ADOBECODEBANC", t = "ABC""#, min_window("ADOBECODEBANC", "ABC"), "BANC");
}

#[test]
fn single() {
    check!(r#"s = "a", t = "a""#, min_window("a", "a"), "a");
}

#[test]
fn impossible() {
    check!(r#"s = "a", t = "aa""#, min_window("a", "aa"), "");
}

#[test]
fn leftmost_tie() {
    check!(r#"s = "abcab", t = "ab""#, min_window("abcab", "ab"), "ab");
}

#[test]
fn duplicates_counted() {
    check!(r#"s = "abaa", t = "aa""#, min_window("abaa", "aa"), "aa");
}
