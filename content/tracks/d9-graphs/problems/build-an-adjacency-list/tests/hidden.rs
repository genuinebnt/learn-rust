use solution::*;

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0, 0)]"#, adjacency_list(1, &[(0, 0)]), vec![vec![0]]);
}

#[test]
fn sorted() {
    check!(r#"n = 4, edges = [(0, 3), (0, 1), (0, 2)]"#, adjacency_list(4, &[(0, 3), (0, 1), (0, 2)])[0].clone(), vec![1, 2, 3]);
}
