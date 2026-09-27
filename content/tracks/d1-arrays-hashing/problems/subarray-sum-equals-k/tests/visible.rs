use solution::*;

#[test]
fn ones() {
    check!(r#"nums = [1, 1, 1], k = 2"#, subarray_sum(&[1, 1, 1], 2), 2);
}

#[test]
fn mixed() {
    check!(r#"nums = [1, 2, 3], k = 3"#, subarray_sum(&[1, 2, 3], 3), 2);
}

#[test]
fn negatives() {
    check!(r#"nums = [1, -1, 0], k = 0"#, subarray_sum(&[1, -1, 0], 0), 3);
}

#[test]
fn none() {
    check!(r#"nums = [5, 5], k = 3"#, subarray_sum(&[5, 5], 3), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5], k = 5"#, subarray_sum(&[5], 5), 1);
}
