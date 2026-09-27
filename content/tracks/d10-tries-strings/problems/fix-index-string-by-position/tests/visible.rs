use solution::*;

#[test]
fn ascii() {
    check!(r#"word = "hello", i = 1"#, nth_letter("hello", 1), Some('e'));
}

#[test]
fn past_the_end() {
    check!(r#"word = "hello", i = 5"#, nth_letter("hello", 5), None);
}

#[test]
fn empty() {
    check!(r#"word = "", i = 0"#, nth_letter("", 0), None);
}

#[test]
fn accented_letter() {
    check!(r#"word = "héllo", i = 1"#, nth_letter("héllo", 1), Some('é'));
}

#[test]
fn after_an_accent() {
    check!(r#"word = "héllo", i = 2 (é is 2 bytes, but 1 character)"#, nth_letter("héllo", 2), Some('l'));
}

#[test]
fn last_character() {
    check!(r#"word = "héllo", i = 4 (5 characters, 6 bytes)"#, nth_letter("héllo", 4), Some('o'));
}
