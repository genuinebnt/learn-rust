#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
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
        todo!()
    }

    pub fn search(&self, word: &str) -> bool {
        todo!()
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        todo!()
    }
}
