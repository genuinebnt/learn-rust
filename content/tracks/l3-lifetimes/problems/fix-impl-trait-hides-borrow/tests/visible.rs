use solution::*;

#[test]
fn filters() {
    check!(r#""a quick brown fox", 3"#, long_words("a quick brown fox", 3).collect::<Vec<_>>(), vec!["quick".to_string(), "brown".to_string()]);
}

#[test]
fn none() {
    check!(r#""a b", 5"#, long_words("a b", 5).count(), 0);
}
