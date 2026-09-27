use solution::*;

#[test]
fn empty() {
    check!(r#"s = "", t = """#, is_anagram("", ""), true);
}

#[test]
fn same_letters_different_counts() {
    check!(r#"s = "aab", t = "abb""#, is_anagram("aab", "abb"), false);
}
