use solution::*;

#[test]
fn leetcode_lls() {
    check!(r#"words = ["abcd", "dcba", "lls", "s", "sssll"]"#, palindrome_pairs(&["abcd", "dcba", "lls", "s", "sssll"]), vec![(0, 1), (1, 0), (2, 4), (3, 2)]);
}

#[test]
fn leetcode_bat_tab() {
    check!(r#"words = ["bat", "tab", "cat"]"#, palindrome_pairs(&["bat", "tab", "cat"]), vec![(0, 1), (1, 0)]);
}

#[test]
fn leetcode_empty_word() {
    check!(r#"words = ["a", ""] ("" pairs with every palindrome, both ways)"#, palindrome_pairs(&["a", ""]), vec![(0, 1), (1, 0)]);
}

#[test]
fn no_words() {
    check!(r#"words = []"#, palindrome_pairs(&[]), Vec::<(usize, usize)>::new());
}

#[test]
fn no_pairs() {
    check!(r#"words = ["a", "b", "c"]"#, palindrome_pairs(&["a", "b", "c"]), Vec::<(usize, usize)>::new());
}

#[test]
fn different_lengths() {
    check!(r#"words = ["race", "car", "ecar"]"#, palindrome_pairs(&["race", "car", "ecar"]), vec![(0, 1), (0, 2), (2, 0)]);
}
