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

    /// The slot with the most hits; the lowest index on a tie; None if there are no slots.
    pub fn busiest(&self) -> Option<usize> {
        let max = *self.hits.iter().max()?;
        self.hits.iter().position(|&h| h == max)
    }
}
