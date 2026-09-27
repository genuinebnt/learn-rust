#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    pass: usize,
    end: usize,
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
        node.pass += 1;
        for b in word.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
            node.pass += 1;
        }
        node.end += 1;
    }

    fn walk(&self, s: &str) -> Option<&Node> {
        let mut node = &self.root;
        for b in s.bytes() {
            node = node.children[(b - b'a') as usize].as_deref()?;
        }
        Some(node)
    }

    pub fn count_words_equal_to(&self, word: &str) -> usize {
        self.walk(word).map_or(0, |n| n.end)
    }

    pub fn count_words_starting_with(&self, prefix: &str) -> usize {
        self.walk(prefix).map_or(0, |n| n.pass)
    }

    pub fn erase(&mut self, word: &str) -> bool {
        let mut node = &mut self.root;
        node.pass = node.pass.saturating_sub(1);
        for b in word.bytes() {
            match node.children[(b - b'a') as usize].as_deref_mut() {
                Some(child) => node = child,
                None => return false,
            }
            node.pass = node.pass.saturating_sub(1);
        }
        node.end = node.end.saturating_sub(1);
        true
    }
}
