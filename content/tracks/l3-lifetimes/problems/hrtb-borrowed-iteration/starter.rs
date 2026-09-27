pub struct Stats<C> {
    data: C,
}

impl<C> Stats<C> {
    pub fn new(data: C) -> Self {
        Stats { data }
    }

    /// The mean, or None if empty.
    pub fn mean(&self) -> Option<f64> {
        todo!()
    }

    /// Largest minus smallest, or None if empty.
    pub fn spread(&self) -> Option<u32> {
        todo!()
    }

    pub fn count_above(&self, threshold: u32) -> usize {
        todo!()
    }
}
