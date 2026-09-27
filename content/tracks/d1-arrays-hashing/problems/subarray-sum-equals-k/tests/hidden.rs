use solution::*;

#[test]
fn none() {
    check!(r#"nums = [5, 5], k = 3"#, subarray_sum(&[5, 5], 3), 0);
}

#[test]
fn all_zero() {
    check!(r#"nums = [0; 100], k = 0"#, subarray_sum(&[0; 100], 0), 5050);
}
