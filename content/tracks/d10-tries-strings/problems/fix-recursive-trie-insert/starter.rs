#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
}

fn idx(b: u8) -> usize {
    (b - b'a') as usize
}

/// Walks to the node for `word`, creating missing nodes on the way.
fn node_for<'a>(node: &'a mut Node, word: &[u8]) -> &'a mut Node {
    let Some((&b, rest)) = word.split_first() else {
        return node;
    };
    if let Some(child) = node.children[idx(b)].as_mut() {
        return node_for(child, rest);
    }
    node.children[idx(b)] = Some(Box::new(Node::default()));
    node_for(node.children[idx(b)].as_mut().unwrap(), rest)
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
        node_for(&mut self.root, word.as_bytes()).end = true;
    }

    pub fn contains(&self, word: &str) -> bool {
        let mut node = &self.root;
        for &b in word.as_bytes() {
            match &node.children[idx(b)] {
                Some(child) => node = child,
                None => return false,
            }
        }
        node.end
    }
}
