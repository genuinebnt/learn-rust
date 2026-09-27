use solution::*;

#[test]
fn no_sep() {
    check!(r#""abc", ",""#, Splitter::new("abc", ",").parts(), vec!["abc"]);
}
