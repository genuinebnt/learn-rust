use solution::*;

#[test]
fn one_one() {
    check!(r#"mat = [[0,0,0],[0,1,0],[0,0,0]]"#, update_matrix(&[vec![0, 0, 0], vec![0, 1, 0], vec![0, 0, 0]]), vec![vec![0, 0, 0], vec![0, 1, 0], vec![0, 0, 0]]);
}

#[test]
fn two_steps_away() {
    check!(r#"mat = [[0,0,0],[0,1,0],[1,1,1]]"#, update_matrix(&[vec![0, 0, 0], vec![0, 1, 0], vec![1, 1, 1]]), vec![vec![0, 0, 0], vec![0, 1, 0], vec![1, 2, 1]]);
}

#[test]
fn single_zero() {
    check!(r#"mat = [[0]]"#, update_matrix(&[vec![0]]), vec![vec![0]]);
}

#[test]
fn one_row() {
    check!(r#"mat = [[1,1,0]]"#, update_matrix(&[vec![1, 1, 0]]), vec![vec![2, 1, 0]]);
}

#[test]
fn no_diagonal_steps() {
    check!(r#"mat = [[0,1],[1,1]]"#, update_matrix(&[vec![0, 1], vec![1, 1]]), vec![vec![0, 1], vec![1, 2]]);
}
