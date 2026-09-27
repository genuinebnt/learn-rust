pub struct Counter {
    hits: Vec<u32>,
}

impl Counter {
    pub fn new(slots: usize) -> Self {
        todo!()
    }

    pub fn hit(&mut self, slot: usize) {
        todo!()
    }

    pub fn total(&self) -> u32 {
        todo!()
    }

    /// The slot with the most hits; the lowest index on a tie; None if there are no slots.
    pub fn busiest(&self) -> Option<usize> {
        todo!()
    }
}
