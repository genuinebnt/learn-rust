pub struct UnionFind {
    parent: Vec<usize>,
    size: Vec<usize>,
    sets: usize,
}

impl UnionFind {
    pub fn new(n: usize) -> Self {
        UnionFind { parent: (0..n).collect(), size: vec![1; n], sets: n }
    }

    pub fn find(&mut self, x: usize) -> usize {
        let p = self.parent[x];
        if p != x {
            self.parent[x] = self.find(p);
        }
        self.parent[x]
    }

    pub fn union(&mut self, a: usize, b: usize) -> bool {
        let (ra, rb) = (self.find(a), self.find(b));
        if ra == rb {
            return false;
        }
        self.parent[ra] = rb;
        self.size[rb] += self.size[ra];
        self.sets -= 1;
        true
    }

    pub fn connected(&mut self, a: usize, b: usize) -> bool {
        self.find(a) == self.find(b)
    }

    pub fn set_size(&mut self, x: usize) -> usize {
        let r = self.find(x);
        self.size[r]
    }

    pub fn set_count(&self) -> usize {
        self.sets
    }
}
