use solution::*;

#[test]
fn leetcode_positive_run() {
    check!(r#"nums = [2, 3, -2, 4]"#, max_product(&[2, 3, -2, 4]), Some(6));
}

#[test]
fn leetcode_zero() {
    check!(r#"nums = [-2, 0, -1]"#, max_product(&[-2, 0, -1]), Some(0));
}

#[test]
fn empty() {
    check!(r#"nums = []"#, max_product(&[]), None);
}

#[test]
fn single_negative() {
    check!(r#"nums = [-2]"#, max_product(&[-2]), Some(-2));
}

#[test]
fn two_negatives_cancel() {
    check!(r#"nums = [-2, 3, -4]"#, max_product(&[-2, 3, -4]), Some(24));
}
