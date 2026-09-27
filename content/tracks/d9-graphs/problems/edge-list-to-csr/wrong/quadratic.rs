pub struct Csr {
    offsets: Vec<usize>,
    targets: Vec<usize>,
}

impl Csr {
    pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
        let mut offsets = vec![0];
        let mut targets = Vec::new();
        for u in 0..n {
            for &(a, b) in edges {
                if a == u {
                    targets.push(b);
                }
            }
            offsets.push(targets.len());
        }
        Csr { offsets, targets }
    }

    pub fn neighbors(&self, u: usize) -> &[usize] {
        &self.targets[self.offsets[u]..self.offsets[u + 1]]
    }

    /// (offsets, targets)
    pub fn parts(&self) -> (&[usize], &[usize]) {
        (&self.offsets, &self.targets)
    }
}
