#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
}

/// Length of the shortest root that `word` starts with.
fn shortest_root(root: &Node, word: &str) -> Option<usize> {
    let mut node = root;
    for (i, b) in word.bytes().enumerate() {
        node = node.children[(b - b'a') as usize].as_deref()?;
        if node.end {
            return Some(i + 1);
        }
    }
    None
}

pub fn replace_words(roots: &[&str], sentence: &str) -> String {
    let mut trie = Node::default();
    for r in roots {
        let mut node = &mut trie;
        for b in r.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
        node.end = true;
    }
    sentence
        .split(' ')
        .map(|w| shortest_root(&trie, w).map_or(w, |n| &w[..n]))
        .collect::<Vec<&str>>()
        .join(" ")
}
