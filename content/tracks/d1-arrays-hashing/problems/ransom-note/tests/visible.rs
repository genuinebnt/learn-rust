use solution::*;

#[test]
fn enough() {
    check!(r#"note = "aa", magazine = "aab""#, can_construct("aa", "aab"), true);
}

#[test]
fn not_enough() {
    check!(r#"note = "aa", magazine = "ab""#, can_construct("aa", "ab"), false);
}

#[test]
fn different_letter() {
    check!(r#"note = "a", magazine = "b""#, can_construct("a", "b"), false);
}

#[test]
fn empty_note() {
    check!(r#"note = "", magazine = "abc""#, can_construct("", "abc"), true);
}

#[test]
fn each_letter_used_once() {
    check!(r#"note = "aab", magazine = "baa""#, can_construct("aab", "baa"), true);
}
