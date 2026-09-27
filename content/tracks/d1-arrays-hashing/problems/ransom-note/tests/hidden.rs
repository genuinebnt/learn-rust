use solution::*;

#[test]
fn empty_note() {
    check!(r#"note = "", magazine = """#, can_construct("", ""), true);
}

#[test]
fn missing_letter() {
    check!(r#"note = "z", magazine = "abc""#, can_construct("z", "abc"), false);
}
