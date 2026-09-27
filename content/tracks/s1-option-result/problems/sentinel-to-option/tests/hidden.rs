use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], x = 1"#, find(&[], 1), None);
}

#[test]
fn first() {
    check!(r#"v = [-1, -1], x = -1"#, find(&[-1, -1], -1), Some(0));
}
