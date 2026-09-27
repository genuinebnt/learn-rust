use solution::*;

#[test]
fn two() {
    check!(r#"heights = [[1,2,2],[3,8,2],[5,3,5]]"#, minimum_effort(&[vec![1, 2, 2], vec![3, 8, 2], vec![5, 3, 5]]), 2);
}

#[test]
fn one() {
    check!(r#"heights = [[1,2,3],[3,8,4],[5,3,5]]"#, minimum_effort(&[vec![1, 2, 3], vec![3, 8, 4], vec![5, 3, 5]]), 1);
}

#[test]
fn winding_flat_path() {
    check!(r#"heights = [[1,2,1,1,1],[1,2,1,2,1],[1,2,1,2,1],[1,2,1,2,1],[1,1,1,2,1]]"#, minimum_effort(&[vec![1, 2, 1, 1, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 1, 1, 2, 1]]), 0);
}

#[test]
fn largest_step_not_sum() {
    check!(r#"heights = [[1,3,2]]"#, minimum_effort(&[vec![1, 3, 2]]), 2);
}

#[test]
fn path_may_turn_back() {
    check!(r#"heights = [[1,1,1],[9,9,1],[1,1,1],[1,9,9],[1,1,1]]"#, minimum_effort(&[vec![1, 1, 1], vec![9, 9, 1], vec![1, 1, 1], vec![1, 9, 9], vec![1, 1, 1]]), 0);
}
