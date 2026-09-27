use solution::*;

#[test]
fn found() {
    check!(r#"pattern = "ab", s = "eidbaooo""#, check_inclusion("ab", "eidbaooo"), true);
}

#[test]
fn not_found() {
    check!(r#"pattern = "ab", s = "eidboaoo""#, check_inclusion("ab", "eidboaoo"), false);
}

#[test]
fn single_match() {
    check!(r#"pattern = "a", s = "a""#, check_inclusion("a", "a"), true);
}

#[test]
fn longer_pattern() {
    check!(r#"pattern = "abc", s = "ab""#, check_inclusion("abc", "ab"), false);
}

#[test]
fn counts_matter() {
    check!(r#"pattern = "aab", s = "abbab""#, check_inclusion("aab", "abbab"), false);
}
