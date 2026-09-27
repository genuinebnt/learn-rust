use solution::*;

#[test]
fn four_words() {
    check!(r#"s = "the quick brown fox""#, third_word_len("the quick brown fox"), Some(5));
}

#[test]
fn two_words() {
    check!(r#"s = "hi there""#, third_word_len("hi there"), None);
}

#[test]
fn exactly_three() {
    check!(r#"s = "a bb ccc""#, third_word_len("a bb ccc"), Some(3));
}

#[test]
fn empty_string() {
    check!(r#"s = """#, third_word_len(""), None);
}

#[test]
fn tabs_and_newlines_separate_words() {
    check!(r#"s = "a\tbb\nccc""#, third_word_len("a\tbb\nccc"), Some(3));
}
