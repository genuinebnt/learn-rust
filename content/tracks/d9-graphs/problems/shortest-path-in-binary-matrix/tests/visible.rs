use solution::*;

#[test]
fn diagonal_step() {
    check!(r#"grid = [[0,1],[1,0]]"#, shortest_path_binary_matrix(&[vec![0, 1], vec![1, 0]]), Some(2));
}

#[test]
fn around_the_wall() {
    check!(r#"grid = [[0,0,0],[1,1,0],[1,1,0]]"#, shortest_path_binary_matrix(&[vec![0, 0, 0], vec![1, 1, 0], vec![1, 1, 0]]), Some(4));
}

#[test]
fn start_blocked() {
    check!(r#"grid = [[1,0,0],[1,1,0],[1,1,0]]"#, shortest_path_binary_matrix(&[vec![1, 0, 0], vec![1, 1, 0], vec![1, 1, 0]]), None);
}

#[test]
fn one_cell() {
    check!(r#"grid = [[0]]"#, shortest_path_binary_matrix(&[vec![0]]), Some(1));
}

#[test]
fn end_blocked() {
    check!(r#"grid = [[0,0],[0,1]]"#, shortest_path_binary_matrix(&[vec![0, 0], vec![0, 1]]), None);
}
