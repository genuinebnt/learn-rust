use solution::*;

#[test]
fn square() {
    check!(r#"adj = [[1, 3], [0, 2], [1, 3], [0, 2]]"#, is_bipartite(&[vec![1, 3], vec![0, 2], vec![1, 3], vec![0, 2]]), true);
}

#[test]
fn triangle_inside() {
    check!(r#"adj = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]"#, is_bipartite(&[vec![1, 2, 3], vec![0, 2], vec![0, 1, 3], vec![0, 2]]), false);
}
