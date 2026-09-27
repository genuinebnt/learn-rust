pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
    edges.iter().fold(vec![(0, 0); n], |mut d, &(u, v)| {
        d[u].1 += 1;
        d[v].0 += 1;
        d
    })
}

pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    (0..n).filter(|&u| !edges.iter().any(|&(_, v)| v == u)).collect()
}
