pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
    edges.iter().fold(vec![(0, 0); n], |mut d, &(u, v)| {
        d[u].0 += 1;
        d[v].1 += 1;
        d
    })
}

pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    degrees(n, edges).iter().enumerate().filter(|&(_, &(_, out))| out == 0).map(|(u, _)| u).collect()
}
