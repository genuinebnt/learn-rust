#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    /// Copies of words that pass through (or end at) this node.
    pass: usize,
    /// Copies of words that end here.
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
        if self.count_words_equal_to(word) == 0 {
            return false;
        }
        let mut node = &mut self.root;
        node.pass -= 1;
        for b in word.bytes() {
            let slot = &mut node.children[(b - b'a') as usize];
            // The last copy through this child: drop the whole branch.
            if slot.as_ref().is_some_and(|child| child.pass == 1) {
                *slot = None;
                return true;
            }
            node = slot.as_deref_mut().expect("counted above");
            node.pass -= 1;
        }
        node.end -= 1;
        true
    }
}
