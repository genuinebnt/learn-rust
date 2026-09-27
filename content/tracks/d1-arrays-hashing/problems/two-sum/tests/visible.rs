use solution::*;

#[test]
fn first_two() {
    check!(r#"nums = [2, 7, 11, 15], target = 9"#, two_sum(&[2, 7, 11, 15], 9), Some((0, 1)));
}

#[test]
fn middle() {
    check!(r#"nums = [3, 2, 4], target = 6"#, two_sum(&[3, 2, 4], 6), Some((1, 2)));
}

#[test]
fn same_value_twice() {
    check!(r#"nums = [3, 3], target = 6"#, two_sum(&[3, 3], 6), Some((0, 1)));
}

#[test]
fn no_pair() {
    check!(r#"nums = [1, 2, 3], target = 7"#, two_sum(&[1, 2, 3], 7), None);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, 4, 3, 90], target = 0"#, two_sum(&[-3, 4, 3, 90], 0), Some((0, 2)));
}
