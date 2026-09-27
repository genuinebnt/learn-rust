use solution::*;

#[test]
fn longer_pattern() {
    check!(r#"pattern = "abc", s = "ab""#, check_inclusion("abc", "ab"), false);
}

#[test]
fn whole_string() {
    check!(r#"pattern = "adc", s = "dcda""#, check_inclusion("adc", "dcda"), true);
}
