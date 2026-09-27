use solution::*;

#[test]
fn leetcode_star() {
    check!(r#"graph = [[1, 2, 3], [0], [0], [0]]"#, shortest_path_length(&[vec![1, 2, 3], vec![0], vec![0], vec![0]]), 4);
}

#[test]
fn leetcode_five() {
    check!(r#"graph = [[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]"#, shortest_path_length(&[vec![1], vec![0, 2, 4], vec![1, 3, 4], vec![2], vec![1, 2]]), 4);
}

#[test]
fn single_node() {
    check!(r#"graph = [[]]"#, shortest_path_length(&[vec![]]), 0);
}

#[test]
fn two_nodes() {
    check!(r#"graph = [[1], [0]]"#, shortest_path_length(&[vec![1], vec![0]]), 1);
}

#[test]
fn triangle() {
    check!(r#"graph = [[1, 2], [0, 2], [0, 1]]"#, shortest_path_length(&[vec![1, 2], vec![0, 2], vec![0, 1]]), 2);
}
