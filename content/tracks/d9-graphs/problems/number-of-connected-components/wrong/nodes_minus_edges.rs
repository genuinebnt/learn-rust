pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
    n.saturating_sub(edges.len()).max(1)
}
