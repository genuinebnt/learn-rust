pub struct Csr {
    offsets: Vec<usize>,
    targets: Vec<usize>,
}

impl Csr {
    pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
        todo!()
    }

    pub fn neighbors(&self, u: usize) -> &[usize] {
        todo!()
    }

    /// (offsets, targets)
    pub fn parts(&self) -> (&[usize], &[usize]) {
        (&self.offsets, &self.targets)
    }
}
