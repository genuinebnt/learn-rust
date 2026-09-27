#[derive(Default)]
struct Node {
    /// a..z, then '{' (the byte after 'z') as the separator.
    children: [Option<Box<Node>>; 27],
    /// Largest index of a word whose key passes through here.
    best: usize,
}

pub struct WordFilter {
    root: Node,
}

impl WordFilter {
    pub fn new(words: &[&str]) -> Self {
        let mut root = Node::default();
        for (i, w) in words.iter().enumerate() {
            // For "apple": "{apple", "e{apple", "le{apple", …, "apple{apple".
            for start in 0..=w.len() {
                let mut node = &mut root;
                for b in w[start..].bytes().chain([b'{']).chain(w.bytes()) {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    node.best = i;
                }
            }
        }
        WordFilter { root }
    }

    pub fn f(&self, prefix: &str, suffix: &str) -> Option<usize> {
        let mut node = &self.root;
        for b in suffix.bytes().chain([b'{']).chain(prefix.bytes()) {
            node = node.children[(b - b'a') as usize].as_deref()?;
        }
        Some(node.best)
    }
}
