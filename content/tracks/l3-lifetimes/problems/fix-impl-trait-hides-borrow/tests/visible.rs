use solution::*;

#[test]
fn filters() {
    check!(r#""a quick brown fox", 3"#, long_words("a quick brown fox", 3).collect::<Vec<_>>(), vec!["quick".to_string(), "brown".to_string()]);
}

#[test]
fn none() {
    check!(r#""a b", 5"#, long_words("a b", 5).count(), 0);
}

#[test]
fn empty() {
    check!(r#""", 0"#, long_words("", 0).count(), 0);
}

#[test]
fn strictly_longer() {
    check!(r#""abc abcd", 3"#, long_words("abc abcd", 3).collect::<Vec<_>>(), vec!["abcd".to_string()]);
}

#[test]
fn min_zero_keeps_all() {
    check!(r#""x yy", 0"#, long_words("x yy", 0).collect::<Vec<_>>(), vec!["x".to_string(), "yy".to_string()]);
}
