#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    end: bool,
}

/// Word break with at least two pieces: `ok[i]` is true when w[..i] splits into dictionary words.
fn is_concatenated(root: &Node, w: &[u8]) -> bool {
    let n = w.len();
    let mut ok = vec![false; n + 1];
    ok[0] = true;
    for i in 0..n {
        if !ok[i] {
            continue;
        }
        let mut node = root;
        for j in i..n {
            match node.children[(w[j] - b'a') as usize].as_deref() {
                Some(child) => node = child,
                None => break,
            }
            // A piece w[i..=j]; the one piece that is the whole word doesn't count.
            if node.end && !(i == 0 && j + 1 == n) {
                ok[j + 1] = true;
            }
        }
    }
    ok[n]
}

pub fn find_all_concatenated_words<'a>(words: &[&'a str]) -> Vec<&'a str> {
    let mut root = Node::default();
    for w in words.iter().filter(|w| !w.is_empty()) {
        let mut node = &mut root;
        for b in w.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
        node.end = true;
    }
    words.iter().copied().filter(|w| !w.is_empty() && is_concatenated(&root, w.as_bytes())).collect()
}
