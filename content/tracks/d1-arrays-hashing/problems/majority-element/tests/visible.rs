use solution::*;

#[test]
fn small() {
    check!(r#"nums = [3, 2, 3]"#, majority(&[3, 2, 3]), 3);
}

#[test]
fn longer() {
    check!(r#"nums = [2, 2, 1, 1, 1, 2, 2]"#, majority(&[2, 2, 1, 1, 1, 2, 2]), 2);
}

#[test]
fn single() {
    check!(r#"nums = [1]"#, majority(&[1]), 1);
}

#[test]
fn majority_not_first() {
    check!(r#"nums = [1, 2, 2]"#, majority(&[1, 2, 2]), 2);
}

#[test]
fn negative() {
    check!(r#"nums = [-1, 5, -1]"#, majority(&[-1, 5, -1]), -1);
}
