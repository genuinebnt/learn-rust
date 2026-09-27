use solution::*;

#[test]
fn two() {
    check!(r#"s = "cbaebabacd", p = "abc""#, find_anagrams("cbaebabacd", "abc"), vec![0, 6]);
}

#[test]
fn overlapping() {
    check!(r#"s = "abab", p = "ab""#, find_anagrams("abab", "ab"), vec![0, 1, 2]);
}
