#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    word: Option<usize>,
}

pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
    let mut root = Node::default();
    for (i, w) in words.iter().enumerate() {
        let mut node = &mut root;
        for b in w.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
        node.word = Some(i);
    }
    // Depth-first through nodes that end a word; each one is buildable.
    let mut best = "";
    let mut stack = vec![&root];
    while let Some(node) = stack.pop() {
        for child in node.children.iter().flatten() {
            if let Some(i) = child.word {
                let w = words[i];
                if w.len() > best.len() || (w.len() == best.len() && w < best) {
                    best = w;
                }
                stack.push(child);
            }
        }
    }
    best
}
