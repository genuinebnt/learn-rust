use std::collections::HashMap;

#[derive(Default)]
pub struct TimeMap {
    history: HashMap<String, Vec<(u64, String)>>,
}

impl TimeMap {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set(&mut self, key: &str, value: &str, t: u64) {
        let list = self.history.entry(key.to_string()).or_default();
        list.retain(|(time, _)| *time != t);
        list.push((t, value.to_string()));
    }

    pub fn get(&self, key: &str, t: u64) -> Option<&str> {
        self.history.get(key)?.iter().filter(|(time, _)| *time <= t).max_by_key(|(time, _)| *time).map(|(_, v)| v.as_str())
    }
}
