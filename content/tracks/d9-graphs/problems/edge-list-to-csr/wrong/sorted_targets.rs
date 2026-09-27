pub struct Csr {
    offsets: Vec<usize>,
    targets: Vec<usize>,
}

impl Csr {
    pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
        let mut sorted = edges.to_vec();
        sorted.sort();
        let mut offsets = vec![0; n + 1];
        for &(u, _) in &sorted {
            offsets[u + 1] += 1;
        }
        for i in 0..n {
            offsets[i + 1] += offsets[i];
        }
        Csr { offsets, targets: sorted.into_iter().map(|(_, v)| v).collect() }
    }

    pub fn neighbors(&self, u: usize) -> &[usize] {
        &self.targets[self.offsets[u]..self.offsets[u + 1]]
    }

    /// (offsets, targets)
    pub fn parts(&self) -> (&[usize], &[usize]) {
        (&self.offsets, &self.targets)
    }
}
