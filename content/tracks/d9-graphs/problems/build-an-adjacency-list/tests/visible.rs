use solution::*;

#[test]
fn small() {
    check!(r#"n = 4, edges = [(0, 1), (2, 1), (1, 0)]"#, adjacency_list(4, &[(0, 1), (2, 1), (1, 0)]), vec![vec![1], vec![0, 2], vec![1], vec![]]);
}

#[test]
fn no_edges() {
    check!(r#"n = 2, edges = []"#, adjacency_list(2, &[]), vec![Vec::<usize>::new(), vec![]]);
}

#[test]
fn repeated_edge() {
    check!(r#"n = 3, edges = [(0, 2), (2, 0), (0, 2)]"#, adjacency_list(3, &[(0, 2), (2, 0), (0, 2)]), vec![vec![2], vec![], vec![0]]);
}

#[test]
fn neighbours_sorted() {
    check!(r#"n = 4, edges = [(0, 3), (0, 1), (0, 2)]"#, adjacency_list(4, &[(0, 3), (0, 1), (0, 2)]), vec![vec![1, 2, 3], vec![0], vec![0], vec![0]]);
}

#[test]
fn self_loop_once() {
    check!(r#"n = 2, edges = [(1, 1), (0, 1)]"#, adjacency_list(2, &[(1, 1), (0, 1)]), vec![vec![1], vec![0, 1]]);
}
