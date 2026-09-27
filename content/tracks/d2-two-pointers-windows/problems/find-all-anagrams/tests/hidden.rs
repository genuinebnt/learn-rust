use solution::*;

#[test]
fn none() {
    check!(r#"s = "aaaa", p = "b""#, find_anagrams("aaaa", "b"), Vec::<usize>::new());
}

#[test]
fn longer_pattern() {
    check!(r#"s = "a", p = "ab""#, find_anagrams("a", "ab"), Vec::<usize>::new());
}
