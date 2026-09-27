use solution::*;

#[test]
fn three() {
    check!(r#"parts = ["a", "bb", "ccc"], sep = ", ""#, { let s = join_with(&["a", "bb", "ccc"], ", "); (s.clone(), s.capacity() == s.len()) }, ("a, bb, ccc".to_string(), true));
}

#[test]
fn one() {
    check!(r#"parts = ["solo"], sep = "-""#, { let s = join_with(&["solo"], "-"); (s.clone(), s.capacity() == s.len()) }, ("solo".to_string(), true));
}
