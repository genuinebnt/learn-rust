use solution::*;

#[test]
fn diamond() {
    check!(r#"adj = [[1, 2], [3], [3], []], start = 0"#, dfs_order(&[vec![1, 2], vec![3], vec![3], vec![]], 0), vec![0, 1, 3, 2]);
}

#[test]
fn not_bfs() {
    check!(r#"adj = [[1, 2], [3], [], []], start = 0"#, dfs_order(&[vec![1, 2], vec![3], vec![], vec![]], 0), vec![0, 1, 3, 2]);
}
