use std::collections::HashMap;

#[derive(Default)]
pub struct MapSum {
    values: HashMap<String, i32>,
}

impl MapSum {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, key: &str, val: i32) {
        self.values.insert(key.to_string(), val);
    }

    pub fn sum(&self, prefix: &str) -> i64 {
        self.values.iter().filter(|(k, _)| k.starts_with(prefix)).map(|(_, &v)| i64::from(v)).sum()
    }
}
