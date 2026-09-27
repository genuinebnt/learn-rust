pub fn find_min_height_trees(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    let mut degree = vec![0usize; n];
    for &(a, b) in edges {
        degree[a] += 1;
        degree[b] += 1;
    }
    let best = degree.iter().copied().max().unwrap_or(0);
    (0..n).filter(|&u| degree[u] == best).collect()
}
