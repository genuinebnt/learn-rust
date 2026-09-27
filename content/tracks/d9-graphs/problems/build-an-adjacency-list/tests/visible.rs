use solution::*;

#[test]
fn small() {
    check!(r#"n = 4, edges = [(0, 1), (2, 1), (1, 0)]"#, adjacency_list(4, &[(0, 1), (2, 1), (1, 0)]), vec![vec![1], vec![0, 2], vec![1], vec![]]);
}

#[test]
fn no_edges() {
    check!(r#"n = 2, edges = []"#, adjacency_list(2, &[]), vec![Vec::<usize>::new(), vec![]]);
}
