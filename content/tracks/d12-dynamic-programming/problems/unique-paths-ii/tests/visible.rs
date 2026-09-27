use solution::*;

#[test]
fn leetcode_center_rock() {
    check!(r#"grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]"#, unique_paths_with_obstacles(&[vec![0, 0, 0], vec![0, 1, 0], vec![0, 0, 0]]), 2);
}

#[test]
fn leetcode_two_by_two() {
    check!(r#"grid = [[0, 1], [0, 0]]"#, unique_paths_with_obstacles(&[vec![0, 1], vec![0, 0]]), 1);
}

#[test]
fn one_free_cell() {
    check!(r#"grid = [[0]]"#, unique_paths_with_obstacles(&[vec![0]]), 1);
}

#[test]
fn one_blocked_cell() {
    check!(r#"grid = [[1]]"#, unique_paths_with_obstacles(&[vec![1]]), 0);
}

#[test]
fn start_blocked() {
    check!(r#"grid = [[1, 0], [0, 0]]"#, unique_paths_with_obstacles(&[vec![1, 0], vec![0, 0]]), 0);
}

#[test]
fn end_blocked() {
    check!(r#"grid = [[0, 0], [0, 1]]"#, unique_paths_with_obstacles(&[vec![0, 0], vec![0, 1]]), 0);
}
