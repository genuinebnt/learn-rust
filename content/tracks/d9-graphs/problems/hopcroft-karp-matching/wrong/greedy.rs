pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
    let mut used_l = vec![false; left];
    let mut used_r = vec![false; right];
    let mut size = 0;
    for &(u, v) in edges {
        if !used_l[u] && !used_r[v] {
            used_l[u] = true;
            used_r[v] = true;
            size += 1;
        }
    }
    size
}
