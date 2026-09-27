#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
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
        let mut node = &self.root;
        for b in pattern.bytes() {
            let next = if b == b'.' { node.children.iter().flatten().next() } else { node.children[(b - b'a') as usize].as_ref() };
            match next {
                Some(child) => node = child,
                None => return false,
            }
        }
        node.end
    }
}
