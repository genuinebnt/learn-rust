use solution::*;

#[test]
fn unicode() {
    check!(r#""héllo hi", 4"#, long_words("héllo hi", 4).collect::<Vec<_>>(), vec!["héllo".to_string()]);
}
