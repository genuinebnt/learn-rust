use std::collections::HashMap;

#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    /// Sum of the values of every key at or below this node.
    total: i64,
}

#[derive(Default)]
pub struct MapSum {
    root: Node,
    values: HashMap<String, i32>,
}

impl MapSum {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, key: &str, val: i32) {
        let old = self.values.insert(key.to_string(), val).unwrap_or(0);
        let delta = i64::from(val) - i64::from(old);
        let mut node = &mut self.root;
        node.total += delta;
        for b in key.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
            node.total += delta;
        }
    }

    pub fn sum(&self, prefix: &str) -> i64 {
        let mut node = &self.root;
        for b in prefix.bytes() {
            match &node.children[(b - b'a') as usize] {
                Some(child) => node = child,
                None => return 0,
            }
        }
        node.total
    }
}
