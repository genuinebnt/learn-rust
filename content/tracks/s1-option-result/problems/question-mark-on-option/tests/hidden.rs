use solution::*;

#[test]
fn extra_spaces() {
    check!(r#"s = "  a  bb   ccc ""#, third_word_len("  a  bb   ccc "), Some(3));
}

#[test]
fn empty() {
    check!(r#"s = """#, third_word_len(""), None);
}
