use solution::*;

#[test]
fn leetcode_three_by_three() {
    check!(r#"grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]"#, min_path_sum(&[vec![1, 3, 1], vec![1, 5, 1], vec![4, 2, 1]]), 7);
}

#[test]
fn leetcode_two_by_three() {
    check!(r#"grid = [[1, 2, 3], [4, 5, 6]]"#, min_path_sum(&[vec![1, 2, 3], vec![4, 5, 6]]), 12);
}

#[test]
fn one_cell() {
    check!(r#"grid = [[5]]"#, min_path_sum(&[vec![5]]), 5);
}

#[test]
fn one_row() {
    check!(r#"grid = [[1, 2, 3]]"#, min_path_sum(&[vec![1, 2, 3]]), 6);
}

#[test]
fn one_column() {
    check!(r#"grid = [[1], [2], [3]]"#, min_path_sum(&[vec![1], vec![2], vec![3]]), 6);
}
