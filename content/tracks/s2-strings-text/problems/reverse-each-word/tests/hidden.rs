use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀x""#, reverse_each_word("🦀x"), "x🦀".to_string());
}

#[test]
fn extra_spaces() {
    check!(r#""  a   bc ""#, reverse_each_word("  a   bc "), "a cb".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, reverse_each_word(""), String::new());
}
