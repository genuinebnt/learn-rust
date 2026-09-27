use solution::*;

#[test]
fn found() {
    check!(r#"pattern = "ab", s = "eidbaooo""#, check_inclusion("ab", "eidbaooo"), true);
}

#[test]
fn not_found() {
    check!(r#"pattern = "ab", s = "eidboaoo""#, check_inclusion("ab", "eidboaoo"), false);
}
