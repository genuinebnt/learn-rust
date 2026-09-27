use solution::*;

#[test]
fn classic() {
    check!(r#"["eat", "tea", "tan", "ate", "nat", "bat"]"#, group_anagrams(&["eat", "tea", "tan", "ate", "nat", "bat"]), vec![vec!["ate", "eat", "tea"], vec!["bat"], vec!["nat", "tan"]]);
}

#[test]
fn empty_string() {
    check!(r#"[""]"#, group_anagrams(&[""]), vec![vec![""]]);
}

#[test]
fn single_letters() {
    check!(r#"["a", "b", "a"]"#, group_anagrams(&["a", "b", "a"]), vec![vec!["a", "a"], vec!["b"]]);
}

#[test]
fn repeat_counts_matter() {
    check!(r#"["a", "aa"]"#, group_anagrams(&["a", "aa"]), vec![vec!["a"], vec!["aa"]]);
}

#[test]
fn no_words() {
    check!(r#"[]"#, group_anagrams(&[]), Vec::<Vec<String>>::new());
}

#[test]
fn leetcode_single_letter() {
    check!(r#"["a"]"#, group_anagrams(&["a"]), vec![vec!["a"]]);
}
