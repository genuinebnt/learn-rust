use solution::*;

#[test]
fn none() {
    check!(r#"parts = [], sep = ",""#, join_with(&[], ","), "");
}

#[test]
fn many() {
    check!(r#"100 parts of "xyz", sep = "/""#, { let parts = vec!["xyz"; 100]; let s = join_with(&parts, "/"); (s.len(), s.capacity() == s.len()) }, (399, true));
}
