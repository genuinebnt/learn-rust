use solution::*;

#[test]
fn leetcode_example() {
    let mut s = KthLargest::new(3, &[4, 5, 8, 2]);
    check!(r#"k = 3, nums = [4, 5, 8, 2]; add 3, 5, 10, 9, 4"#, [3, 5, 10, 9, 4].map(|v| s.add(v)), [Some(4), Some(5), Some(5), Some(8), Some(8)]);
}

#[test]
fn leetcode_duplicates_count() {
    let mut s = KthLargest::new(4, &[7, 7, 7, 7, 8, 3]);
    check!(r#"k = 4, nums = [7, 7, 7, 7, 8, 3]; add 2, 10, 9, 9"#, [2, 10, 9, 9].map(|v| s.add(v)), [Some(7), Some(7), Some(7), Some(8)]);
}

#[test]
fn none_until_k_values() {
    let mut s = KthLargest::new(3, &[]);
    check!(r#"k = 3, nums = []; add 1, 2, 3, 4"#, [1, 2, 3, 4].map(|v| s.add(v)), [None, None, Some(1), Some(2)]);
}

#[test]
fn k_one_is_the_maximum() {
    let mut s = KthLargest::new(1, &[5]);
    check!(r#"k = 1, nums = [5]; add 3, 9, 2"#, [3, 9, 2].map(|v| s.add(v)), [Some(5), Some(9), Some(9)]);
}

#[test]
fn negatives() {
    let mut s = KthLargest::new(2, &[-5, -1]);
    check!(r#"k = 2, nums = [-5, -1]; add -3, -10, 0"#, [-3, -10, 0].map(|v| s.add(v)), [Some(-3), Some(-3), Some(-1)]);
}
