use solution::*;

#[test]
fn four_numbers() {
    check!(r#"nums = [1, 2, 3, 4]"#, running_sum(&[1, 2, 3, 4]), vec![1, 3, 6, 10]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, running_sum(&[]), Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, running_sum(&[5]), vec![5]);
}

#[test]
fn negatives() {
    check!(r#"nums = [3, -1, -2]"#, running_sum(&[3, -1, -2]), vec![3, 2, 0]);
}

#[test]
fn zeros_keep_the_total() {
    check!(r#"nums = [2, 0, 0, 1]"#, running_sum(&[2, 0, 0, 1]), vec![2, 2, 2, 3]);
}

#[test]
fn leetcode_ones() {
    check!(r#"nums = [1, 1, 1, 1, 1]"#, running_sum(&[1, 1, 1, 1, 1]), vec![1, 2, 3, 4, 5]);
}

#[test]
fn leetcode_mixed() {
    check!(r#"nums = [3, 1, 2, 10, 1]"#, running_sum(&[3, 1, 2, 10, 1]), vec![3, 4, 6, 16, 17]);
}
