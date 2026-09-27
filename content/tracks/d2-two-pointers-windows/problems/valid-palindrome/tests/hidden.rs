use solution::*;

#[test]
fn digits_matter() {
    check!(r#"s = "0P""#, is_palindrome("0P"), false);
}

#[test]
fn empty() {
    check!(r#"s = """#, is_palindrome(""), true);
}
