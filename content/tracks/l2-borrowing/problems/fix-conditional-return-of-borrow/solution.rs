use std::collections::HashMap;

#[derive(Default)]
pub struct Node {
    pub count: u32,
    pub kids: HashMap<char, Node>,
}

/// The node reached by following `path` from `root` as far as it exists (the root when even the first char
/// is missing).
pub fn deepest_mut<'a>(root: &'a mut Node, path: &str) -> &'a mut Node {
    let mut cur = root;
    for c in path.chars() {
        if !cur.kids.contains_key(&c) {
            break;
        }
        cur = cur.kids.get_mut(&c).unwrap();
    }
    cur
}

/// Extends the trie by one node along `path` from the deepest existing node, bumps that node's count, and
/// returns it. When the whole path already exists, bumps its end node.
pub fn grow<'a>(root: &'a mut Node, path: &str) -> &'a mut Node {
    let depth = depth_of(root, path);
    let node = deepest_mut(root, path);
    let node = match path.chars().nth(depth) {
        Some(c) => node.kids.entry(c).or_default(),
        None => node,
    };
    node.count += 1;
    node
}

fn depth_of(root: &Node, path: &str) -> usize {
    let mut cur = root;
    let mut depth = 0;
    for c in path.chars() {
        match cur.kids.get(&c) {
            Some(next) => cur = next,
            None => break,
        }
        depth += 1;
    }
    depth
}

/// The first word longer than `n` bytes; otherwise pushes "fallback" and returns that.
pub fn first_long_or_push(words: &mut Vec<String>, n: usize) -> &mut String {
    match words.iter().position(|w| w.len() > n) {
        Some(i) => &mut words[i],
        None => {
            words.push("fallback".to_string());
            words.last_mut().unwrap()
        }
    }
}
