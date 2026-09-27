use solution::*;

#[test]
fn first_word_slices_input() {
    let s = "  hello world";
    let w = first_word(s);
    check!(r#"first_word("  hello world")"#, (w, w.as_ptr() == s[2..].as_ptr()), ("hello", true));
}

#[test]
fn extension_cases() {
    let owned: Vec<String> = ["a/b.tar.gz", ".bashrc", "x.", "dir.d/file"].iter().map(|s| s.to_string()).collect();
    check!(r#"extension of "a/b.tar.gz", ".bashrc", "x.", "dir.d/file""#, owned.iter().map(|p| extension(p)).collect::<Vec<_>>(), vec![Some("gz"), None, Some(""), None]);
}

#[test]
fn join_str_and_string_slices() {
    let owned = vec!["x".to_string(), "y".to_string()];
    check!(r#"join_nonempty(["a", "", "b"], "-") and of Strings ["x", "y"]"#, (join_nonempty(&["a", "", "b"], "-"), join_nonempty(&owned, ", ")), ("a-b".to_string(), "x, y".to_string()));
}

#[test]
fn count_from_split() {
    check!(r#"count_word("The cat saw the THE".split_whitespace(), "the")"#, count_word("The cat saw the THE".split_whitespace(), "the"), 3);
}

#[test]
fn count_owned_and_borrowed() {
    let words = vec!["a".to_string(), "b".to_string(), "A".to_string()];
    check!(r#"count_word(&words, "a"), then count_word(words, "b")"#, (count_word(&words, "a"), count_word(words, "b")), (2, 1));
}
