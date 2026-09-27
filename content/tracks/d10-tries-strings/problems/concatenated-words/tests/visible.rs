use solution::*;

#[test]
fn leetcode_cats_and_dogs() {
    check!(r#"words = ["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"]"#, find_all_concatenated_words(&["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"]), vec!["catsdogcats", "dogcatsdog", "ratcatdogcat"]);
}

#[test]
fn leetcode_catdog() {
    check!(r#"words = ["cat", "dog", "catdog"]"#, find_all_concatenated_words(&["cat", "dog", "catdog"]), vec!["catdog"]);
}

#[test]
fn empty() {
    check!(r#"words = []"#, find_all_concatenated_words(&[]), Vec::<&str>::new());
}

#[test]
fn one_word_is_not_enough() {
    check!(r#"words = ["a"] (a word alone is one piece)"#, find_all_concatenated_words(&["a"]), Vec::<&str>::new());
}

#[test]
fn same_piece_twice() {
    check!(r#"words = ["a", "aaa"]"#, find_all_concatenated_words(&["a", "aaa"]), vec!["aaa"]);
}

#[test]
fn empty_string_is_no_piece() {
    check!(r#"words = ["", "a", "aa"]"#, find_all_concatenated_words(&["", "a", "aa"]), vec!["aa"]);
}
