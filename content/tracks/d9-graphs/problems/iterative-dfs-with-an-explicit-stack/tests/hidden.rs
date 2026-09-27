use solution::*;

#[test]
fn cycle() {
    check!(r#"adj = [[1], [2], [0]], start = 1"#, dfs_order(&[vec![1], vec![2], vec![0]], 1), vec![1, 2, 0]);
}

#[test]
fn long_path() {
    let adj: Vec<Vec<usize>> = (0..200_000).map(|i| if i + 1 < 200_000 { vec![i + 1] } else { vec![] }).collect();
    let order = dfs_order(&adj, 0);
    check!(r#"path 0 → 1 → … → 199999"#, (order.len(), order.last().copied()), (200_000, Some(199_999)));
}
