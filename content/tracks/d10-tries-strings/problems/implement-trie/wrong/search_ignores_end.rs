#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
}

#[derive(Default)]
pub struct Trie {
    root: Node,
}

impl Trie {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&mut self, word: &str) {
        let mut node = &mut self.root;
        for b in word.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
    }

    fn walk(&self, s: &str) -> Option<&Node> {
        let mut node = &self.root;
        for b in s.bytes() {
            node = node.children[(b - b'a') as usize].as_deref()?;
        }
        Some(node)
    }

    pub fn search(&self, word: &str) -> bool {
        self.walk(word).is_some()
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        self.walk(prefix).is_some()
    }
}
