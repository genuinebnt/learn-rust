use solution::*;

#[test]
fn no_words() {
    check!(r#"[]"#, group_anagrams(&[]), Vec::<Vec<String>>::new());
}

#[test]
fn duplicates() {
    check!(r#"["ab", "ba", "ab"]"#, group_anagrams(&["ab", "ba", "ab"]), vec![vec!["ab", "ab", "ba"]]);
}
