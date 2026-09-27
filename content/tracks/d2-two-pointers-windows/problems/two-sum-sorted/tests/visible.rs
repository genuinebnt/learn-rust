use solution::*;

#[test]
fn first_two() {
    check!(r#"nums = [2, 7, 11, 15], target = 9"#, two_sum_sorted(&[2, 7, 11, 15], 9), Some((0, 1)));
}

#[test]
fn outer() {
    check!(r#"nums = [2, 3, 4], target = 6"#, two_sum_sorted(&[2, 3, 4], 6), Some((0, 2)));
}

#[test]
fn none() {
    check!(r#"nums = [1, 2], target = 5"#, two_sum_sorted(&[1, 2], 5), None);
}

#[test]
fn negative() {
    check!(r#"nums = [-1, 0], target = -1"#, two_sum_sorted(&[-1, 0], -1), Some((0, 1)));
}

#[test]
fn empty() {
    check!(r#"nums = [], target = 0"#, two_sum_sorted(&[], 0), None);
}
