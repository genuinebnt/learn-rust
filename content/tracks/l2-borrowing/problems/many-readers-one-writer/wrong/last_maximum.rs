pub struct Counter {
    hits: Vec<u32>,
}

impl Counter {
    pub fn new(slots: usize) -> Self {
        Counter { hits: vec![0; slots] }
    }

    pub fn hit(&mut self, slot: usize) {
        self.hits[slot] += 1;
    }

    pub fn total(&self) -> u32 {
        self.hits.iter().sum()
    }

    pub fn busiest(&self) -> Option<usize> {
        self.hits.iter().enumerate().max_by_key(|&(_, h)| *h).map(|(i, _)| i)
    }
}
