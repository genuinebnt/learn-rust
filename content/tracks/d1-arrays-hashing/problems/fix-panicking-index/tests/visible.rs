use solution::*;

#[test]
fn in_range() {
    check!(r#"v = [4, 5, 6], i = 1"#, nth_or_zero(&[4, 5, 6], 1), 5);
}

#[test]
fn past_the_end() {
    check!(r#"v = [4, 5, 6], i = 3"#, nth_or_zero(&[4, 5, 6], 3), 0);
}

#[test]
fn empty() {
    check!(r#"v = [], i = 0"#, nth_or_zero(&[], 0), 0);
}
