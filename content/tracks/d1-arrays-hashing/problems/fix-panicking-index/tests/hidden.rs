use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], i = 0"#, nth_or_zero(&[], 0), 0);
}

#[test]
fn huge_index() {
    check!(r#"v = [1], i = usize::MAX"#, nth_or_zero(&[1], usize::MAX), 0);
}
