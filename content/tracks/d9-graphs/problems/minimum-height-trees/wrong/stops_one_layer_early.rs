pub fn find_min_height_trees(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    if n <= 2 {
        return (0..n).collect();
    }
    let mut adj = vec![Vec::new(); n];
    let mut degree = vec![0usize; n];
    for &(a, b) in edges {
        adj[a].push(b);
        adj[b].push(a);
        degree[a] += 1;
        degree[b] += 1;
    }
    let mut leaves: Vec<usize> = (0..n).filter(|&u| degree[u] == 1).collect();
    let mut left = n;
    while left > 3 {
        left -= leaves.len();
        let mut next = Vec::new();
        for &leaf in &leaves {
            for &v in &adj[leaf] {
                degree[v] -= 1;
                if degree[v] == 1 {
                    next.push(v);
                }
            }
        }
        leaves = next;
    }
    leaves.sort_unstable();
    leaves
}
