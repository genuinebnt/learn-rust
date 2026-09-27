use solution::*;

#[test]
fn four_words() {
    check!(r#"s = "the quick brown fox""#, third_word_len("the quick brown fox"), Some(5));
}

#[test]
fn two_words() {
    check!(r#"s = "hi there""#, third_word_len("hi there"), None);
}
