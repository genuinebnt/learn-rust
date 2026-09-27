use solution::*;

#[test]
fn small() {
    check!(r#"nums = [3, 2, 3]"#, majority(&[3, 2, 3]), 3);
}

#[test]
fn longer() {
    check!(r#"nums = [2, 2, 1, 1, 1, 2, 2]"#, majority(&[2, 2, 1, 1, 1, 2, 2]), 2);
}
