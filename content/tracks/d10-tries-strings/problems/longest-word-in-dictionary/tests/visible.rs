use solution::*;

#[test]
fn leetcode_world() {
    check!(r#"words = ["w", "wo", "wor", "worl", "world"]"#, longest_word(&["w", "wo", "wor", "worl", "world"]), "world");
}

#[test]
fn leetcode_tie_goes_to_apple() {
    check!(r#"words = ["a", "banana", "app", "appl", "ap", "apply", "apple"]"#, longest_word(&["a", "banana", "app", "appl", "ap", "apply", "apple"]), "apple");
}

#[test]
fn empty() {
    check!(r#"words = []"#, longest_word(&[]), "");
}

#[test]
fn nothing_buildable() {
    check!(r#"words = ["ab", "abc"] (no one-letter word)"#, longest_word(&["ab", "abc"]), "");
}

#[test]
fn every_prefix_needed() {
    check!(r#"words = ["b", "ab", "abc"] ("a" is missing)"#, longest_word(&["b", "ab", "abc"]), "b");
}

#[test]
fn single_letters_tie() {
    check!(r#"words = ["c", "b", "a"]"#, longest_word(&["c", "b", "a"]), "a");
}
