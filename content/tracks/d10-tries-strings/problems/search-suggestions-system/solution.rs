#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    /// Up to three products below this node, as indexes into the sorted list; the smallest come first.
    top: Vec<usize>,
}

pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
    let mut sorted = products.to_vec();
    sorted.sort_unstable();
    let mut root = Node::default();
    // Sorted order means the first three to reach a node are its three smallest.
    for (i, p) in sorted.iter().enumerate() {
        let mut node = &mut root;
        for b in p.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
            if node.top.len() < 3 {
                node.top.push(i);
            }
        }
    }
    // One cursor, moved one letter per keystroke; `None` once the prefix has fallen off the trie.
    let mut cursor = Some(&root);
    search_word
        .bytes()
        .map(|b| {
            cursor = cursor.and_then(|node| node.children[(b - b'a') as usize].as_deref());
            cursor.map_or_else(Vec::new, |node| node.top.iter().map(|&i| sorted[i].to_string()).collect())
        })
        .collect()
}
