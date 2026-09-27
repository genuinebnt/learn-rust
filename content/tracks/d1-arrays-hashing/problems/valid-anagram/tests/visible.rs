use solution::*;

#[test]
fn anagram() {
    check!(r#"s = "anagram", t = "nagaram""#, is_anagram("anagram", "nagaram"), true);
}

#[test]
fn not_anagram() {
    check!(r#"s = "rat", t = "car""#, is_anagram("rat", "car"), false);
}

#[test]
fn different_lengths() {
    check!(r#"s = "ab", t = "a""#, is_anagram("ab", "a"), false);
}

#[test]
fn same_letters_different_counts() {
    check!(r#"s = "aab", t = "abb""#, is_anagram("aab", "abb"), false);
}

#[test]
fn empty() {
    check!(r#"s = "", t = """#, is_anagram("", ""), true);
}
