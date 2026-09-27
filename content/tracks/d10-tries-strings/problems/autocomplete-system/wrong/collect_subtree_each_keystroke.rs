use std::collections::BTreeMap;

#[derive(Default)]
struct Node {
    children: BTreeMap<char, Node>,
    count: u64,
}

fn collect(node: &Node, path: &mut String, out: &mut Vec<(u64, String)>) {
    if node.count > 0 {
        out.push((node.count, path.clone()));
    }
    for (&c, child) in &node.children {
        path.push(c);
        collect(child, path, out);
        path.pop();
    }
}

pub struct AutocompleteSystem {
    root: Node,
    typed: String,
}

impl AutocompleteSystem {
    pub fn new(sentences: &[&str], times: &[u32]) -> Self {
        let mut sys = AutocompleteSystem { root: Node::default(), typed: String::new() };
        for (s, &t) in sentences.iter().zip(times) {
            sys.add(s, u64::from(t));
        }
        sys
    }

    fn add(&mut self, s: &str, times: u64) {
        let mut node = &mut self.root;
        for c in s.chars() {
            node = node.children.entry(c).or_default();
        }
        node.count += times;
    }

    pub fn input(&mut self, c: char) -> Vec<String> {
        if c == '#' {
            let typed = std::mem::take(&mut self.typed);
            self.add(&typed, 1);
            return Vec::new();
        }
        self.typed.push(c);
        let mut node = &self.root;
        for ch in self.typed.chars() {
            match node.children.get(&ch) {
                Some(n) => node = n,
                None => return Vec::new(),
            }
        }
        let mut all = Vec::new();
        let mut path = self.typed.clone();
        collect(node, &mut path, &mut all);
        all.sort_by(|a, b| b.0.cmp(&a.0).then_with(|| a.1.cmp(&b.1)));
        all.into_iter().take(3).map(|(_, s)| s).collect()
    }
}
