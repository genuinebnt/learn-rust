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
        let max = *self.hits.iter().max()?;
        if max == 0 {
            return None;
        }
        self.hits.iter().position(|&h| h == max)
    }
}
