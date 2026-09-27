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
        self.entries.entry(key.to_string()).or_default().insert(t, value.to_string());
    }

    pub fn get(&self, key: &str, t: u64) -> Option<&str> {
        self.entries.get(key)?.range(..=t).next_back().map(|(_, v)| v.as_str())
    }
}
