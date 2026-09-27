#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    total: i64,
}

#[derive(Default)]
pub struct MapSum {
    root: Node,
}

impl MapSum {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, key: &str, val: i32) {
        let mut node = &mut self.root;
        node.total += i64::from(val);
        for b in key.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
            node.total += i64::from(val);
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
