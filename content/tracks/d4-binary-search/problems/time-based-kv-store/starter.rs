use std::collections::{BTreeMap, HashMap};

#[derive(Default)]
pub struct TimeMap {
    entries: HashMap<String, BTreeMap<u64, String>>,
}

impl TimeMap {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set(&mut self, key: &str, value: &str, t: u64) {
        todo!()
    }

    pub fn get(&self, key: &str, t: u64) -> Option<&str> {
        todo!()
    }
}
