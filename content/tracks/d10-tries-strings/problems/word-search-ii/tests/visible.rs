use solution::*;

#[test]
fn leetcode_oath() {
    check!(r#"board = ["oaan", "etae", "ihkr", "iflv"], words = ["oath", "pea", "eat", "rain"]"#, find_words(&["oaan", "etae", "ihkr", "iflv"], &["oath", "pea", "eat", "rain"]), vec!["eat", "oath"]);
}

#[test]
fn leetcode_cell_used_twice() {
    check!(r#"board = ["ab", "cd"], words = ["abcb"] (spelling it would reuse the b)"#, find_words(&["ab", "cd"], &["abcb"]), Vec::<&str>::new());
}

#[test]
fn no_words() {
    check!(r#"board = ["a"], words = []"#, find_words(&["a"], &[]), Vec::<&str>::new());
}

#[test]
fn sorted_and_once() {
    check!(r#"board = ["ab"], words = ["b", "a", "ab", "a"]"#, find_words(&["ab"], &["b", "a", "ab", "a"]), vec!["a", "ab", "b"]);
}

#[test]
fn path_turns_corners() {
    check!(r#"board = ["ab", "dc"], words = ["abcd", "abdc"] (no diagonal steps)"#, find_words(&["ab", "dc"], &["abcd", "abdc"]), vec!["abcd"]);
}

#[test]
fn each_cell_once_per_word() {
    check!(r#"board = ["aa"], words = ["a", "aa", "aaa"]"#, find_words(&["aa"], &["a", "aa", "aaa"]), vec!["a", "aa"]);
}
