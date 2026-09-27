#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 27],
    best: Option<usize>,
}

pub struct WordFilter {
    root: Node,
}

impl WordFilter {
    pub fn new(words: &[&str]) -> Self {
        let mut root = Node::default();
        for (i, w) in words.iter().enumerate() {
            for start in 0..=w.len() {
                let mut node = &mut root;
                for b in w[start..].bytes().chain([b'{']).chain(w.bytes()) {
                    node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
                    node.best.get_or_insert(i);
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
        node.best
    }
}
