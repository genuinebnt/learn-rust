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
