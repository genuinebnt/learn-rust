use solution::*;

#[test]
fn two() {
    check!(r#"s = "cbaebabacd", p = "abc""#, find_anagrams("cbaebabacd", "abc"), vec![0, 6]);
}

#[test]
fn overlapping() {
    check!(r#"s = "abab", p = "ab""#, find_anagrams("abab", "ab"), vec![0, 1, 2]);
}

#[test]
fn none() {
    check!(r#"s = "aaaa", p = "b""#, find_anagrams("aaaa", "b"), Vec::<usize>::new());
}

#[test]
fn longer_pattern() {
    check!(r#"s = "a", p = "ab""#, find_anagrams("a", "ab"), Vec::<usize>::new());
}

#[test]
fn empty_pattern() {
    check!(r#"s = "abc", p = """#, find_anagrams("abc", ""), Vec::<usize>::new());
}
