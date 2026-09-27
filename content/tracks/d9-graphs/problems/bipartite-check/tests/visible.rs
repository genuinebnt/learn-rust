use solution::*;

#[test]
fn square() {
    check!(r#"adj = [[1, 3], [0, 2], [1, 3], [0, 2]]"#, is_bipartite(&[vec![1, 3], vec![0, 2], vec![1, 3], vec![0, 2]]), true);
}

#[test]
fn triangle_inside() {
    check!(r#"adj = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]"#, is_bipartite(&[vec![1, 2, 3], vec![0, 2], vec![0, 1, 3], vec![0, 2]]), false);
}

#[test]
fn single_edge() {
    check!(r#"adj = [[1], [0]]"#, is_bipartite(&[vec![1], vec![0]]), true);
}

#[test]
fn lone_node() {
    check!(r#"adj = [[]]"#, is_bipartite(&[vec![]]), true);
}

#[test]
fn odd_cycle_in_another_component() {
    check!(r#"adj = [[1], [0], [3, 4], [2, 4], [2, 3]]"#, is_bipartite(&[vec![1], vec![0], vec![3, 4], vec![2, 4], vec![2, 3]]), false);
}
