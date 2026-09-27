pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
    edges.iter().filter(|&&(u, v)| u != v).fold(vec![(0, 0); n], |mut d, &(u, v)| {
        d[u].1 += 1;
        d[v].0 += 1;
        d
    })
}

pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    degrees(n, edges).iter().enumerate().filter(|&(_, &(indeg, _))| indeg == 0).map(|(u, _)| u).collect()
}
