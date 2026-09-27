use solution::*;

#[test]
fn leetcode_eight() {
    check!(r#"nums = [10, 9, 2, 5, 3, 7, 101, 18]"#, length_of_lis(&[10, 9, 2, 5, 3, 7, 101, 18]), 4);
}

#[test]
fn leetcode_six() {
    check!(r#"nums = [0, 1, 0, 3, 2, 3]"#, length_of_lis(&[0, 1, 0, 3, 2, 3]), 4);
}

#[test]
fn leetcode_all_equal() {
    check!(r#"nums = [7, 7, 7, 7, 7, 7, 7]"#, length_of_lis(&[7, 7, 7, 7, 7, 7, 7]), 1);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, length_of_lis(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, length_of_lis(&[5]), 1);
}

#[test]
fn may_skip() {
    check!(r#"nums = [1, 5, 2, 3] (skips the 5)"#, length_of_lis(&[1, 5, 2, 3]), 3);
}
