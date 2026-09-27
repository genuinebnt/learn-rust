use solution::*;

#[test]
fn classic() {
    check!(r#"["eat", "tea", "tan", "ate", "nat", "bat"]"#, group_anagrams(&["eat", "tea", "tan", "ate", "nat", "bat"]), vec![vec!["ate", "eat", "tea"], vec!["bat"], vec!["nat", "tan"]]);
}

#[test]
fn empty_string() {
    check!(r#"[""]"#, group_anagrams(&[""]), vec![vec![""]]);
}
