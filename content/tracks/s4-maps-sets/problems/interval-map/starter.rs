use std::collections::BTreeMap;

pub struct IntervalMap<V> {
    /// start → (end, value)
    by_start: BTreeMap<u32, (u32, V)>,
}

impl<V> IntervalMap<V> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn insert(&mut self, start: u32, end: u32, value: V) -> Result<(), V> {
        todo!()
    }

    pub fn get(&self, point: u32) -> Option<&V> {
        todo!()
    }
}
