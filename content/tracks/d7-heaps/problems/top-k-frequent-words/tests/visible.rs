use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"words = ["i", "love", "leetcode", "i", "love", "coding"], k = 2"#, top_k_frequent(&["i", "love", "leetcode", "i", "love", "coding"], 2), vec!["i", "love"]);
}

#[test]
fn leetcode_four() {
    check!(r#"words = ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], k = 4"#, top_k_frequent(&["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4), vec!["the", "is", "sunny", "day"]);
}

#[test]
fn ties_alphabetical() {
    check!(r#"words = ["b", "c", "a"], k = 2"#, top_k_frequent(&["b", "c", "a"], 2), vec!["a", "b"]);
}

#[test]
fn empty() {
    check!(r#"words = [], k = 3"#, top_k_frequent(&[], 3), Vec::<&str>::new());
}

#[test]
fn k_zero() {
    check!(r#"words = ["a"], k = 0"#, top_k_frequent(&["a"], 0), Vec::<&str>::new());
}

#[test]
fn fewer_words_than_k() {
    check!(r#"words = ["x", "y", "x"], k = 5"#, top_k_frequent(&["x", "y", "x"], 5), vec!["x", "y"]);
}
