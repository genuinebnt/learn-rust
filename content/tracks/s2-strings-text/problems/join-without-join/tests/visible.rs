use solution::*;

#[test]
fn three() {
    check!(r#"words = ["a", "bc", "d"], sep = ", ""#, join_words(&["a", "bc", "d"], ", "), "a, bc, d".to_string());
}

#[test]
fn one() {
    check!(r#"words = ["solo"], sep = "-""#, join_words(&["solo"], "-"), "solo".to_string());
}
