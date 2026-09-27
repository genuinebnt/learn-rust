pub struct IntervalMap<V> {
    items: Vec<(u32, u32, V)>,
}

impl<V> IntervalMap<V> {
    pub fn new() -> Self {
        IntervalMap { items: Vec::new() }
    }

    pub fn insert(&mut self, start: u32, end: u32, value: V) -> Result<(), V> {
        if start >= end || self.items.iter().any(|(s, e, _)| *s < end && start < *e) {
            return Err(value);
        }
        self.items.push((start, end, value));
        Ok(())
    }

    pub fn get(&self, point: u32) -> Option<&V> {
        self.items.iter().find(|(s, e, _)| *s <= point && point < *e).map(|(_, _, v)| v)
    }
}
