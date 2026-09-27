use solution::*;

#[test]
fn single() {
    check!(r#"nums = [9]"#, majority(&[9]), 9);
}

#[test]
fn negative_majority() {
    check!(r#"nums = [-1, 5, -1, -1, 6]"#, majority(&[-1, 5, -1, -1, 6]), -1);
}
