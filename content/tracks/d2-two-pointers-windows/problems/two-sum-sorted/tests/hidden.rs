use solution::*;

#[test]
fn empty() {
    check!(r#"nums = [], target = 0"#, two_sum_sorted(&[], 0), None);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, 0, i32::MAX], target = -1"#, two_sum_sorted(&[i32::MIN, 0, i32::MAX], -1), Some((0, 2)));
}
