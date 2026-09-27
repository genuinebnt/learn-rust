use solution::*;

#[test]
fn odd_cycle_elsewhere() {
    check!(r#"adj = [[], [2, 3], [1, 3], [1, 2]]"#, is_bipartite(&[vec![], vec![2, 3], vec![1, 3], vec![1, 2]]), false);
}

#[test]
fn two_edges() {
    check!(r#"adj = [[1], [0], [3], [2]]"#, is_bipartite(&[vec![1], vec![0], vec![3], vec![2]]), true);
}

#[test]
fn empty() {
    check!(r#"adj = []"#, is_bipartite(&[]), true);
}
