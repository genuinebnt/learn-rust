#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
}

fn matches(node: &Node, pattern: &[u8]) -> bool {
    match pattern.split_first() {
        None => node.end,
        Some((b'.', rest)) => node.children.iter().flatten().any(|child| matches(child, rest)),
        Some((&b, rest)) => node.children[(b - b'a') as usize].as_deref().is_some_and(|child| matches(child, rest)),
    }
}

#[derive(Default)]
pub struct WordDictionary {
    root: Node,
}

impl WordDictionary {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_word(&mut self, word: &str) {
        let mut node = &mut self.root;
        for b in word.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
        node.end = true;
    }

    pub fn search(&self, pattern: &str) -> bool {
        matches(&self.root, pattern.as_bytes())
    }
}
