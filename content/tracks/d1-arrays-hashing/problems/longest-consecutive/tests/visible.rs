use solution::*;

#[test]
fn four() {
    check!(r#"nums = [100, 4, 200, 1, 3, 2]"#, longest_consecutive(&[100, 4, 200, 1, 3, 2]), 4);
}

#[test]
fn nine() {
    check!(r#"nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]"#, longest_consecutive(&[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]), 9);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, longest_consecutive(&[]), 0);
}

#[test]
fn duplicates_inside_run() {
    check!(r#"nums = [1, 2, 2, 3]"#, longest_consecutive(&[1, 2, 2, 3]), 3);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, -2, -1, 5]"#, longest_consecutive(&[-3, -2, -1, 5]), 3);
}

#[test]
fn leetcode_repeat_zero_one() {
    check!(r#"nums = [1, 0, 1, 2]"#, longest_consecutive(&[1, 0, 1, 2]), 3);
}
