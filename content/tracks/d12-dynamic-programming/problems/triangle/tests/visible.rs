use solution::*;

#[test]
fn leetcode_four_rows() {
    check!(r#"triangle = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]"#, minimum_total(&[vec![2], vec![3, 4], vec![6, 5, 7], vec![4, 1, 8, 3]]), 11);
}

#[test]
fn leetcode_one_row() {
    check!(r#"triangle = [[-10]]"#, minimum_total(&[vec![-10]]), -10);
}

#[test]
fn two_rows() {
    check!(r#"triangle = [[1], [2, 3]]"#, minimum_total(&[vec![1], vec![2, 3]]), 3);
}

#[test]
fn cheap_first_step_is_a_trap() {
    check!(r#"triangle = [[1], [2, 3], [100, 100, 1]]"#, minimum_total(&[vec![1], vec![2, 3], vec![100, 100, 1]]), 5);
}

#[test]
fn steps_must_be_adjacent() {
    check!(r#"triangle = [[-1], [2, 3], [1, -1, -3]]"#, minimum_total(&[vec![-1], vec![2, 3], vec![1, -1, -3]]), -1);
}
