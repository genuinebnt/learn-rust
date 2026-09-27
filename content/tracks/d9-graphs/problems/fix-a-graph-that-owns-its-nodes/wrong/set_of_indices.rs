use std::collections::BTreeSet;

#[derive(Default)]
pub struct Graph {
    pub nodes: Vec<Node>,
}

pub struct Node {
    pub name: String,
    pub next: BTreeSet<usize>,
}

impl Graph {
    pub fn new() -> Self {
        Graph::default()
    }

    pub fn add_node(&mut self, name: &str) -> usize {
        self.nodes.push(Node { name: name.to_string(), next: BTreeSet::new() });
        self.nodes.len() - 1
    }

    pub fn add_edge(&mut self, from: usize, to: usize) {
        self.nodes[from].next.insert(to);
    }

    pub fn neighbors(&self, u: usize) -> Vec<&str> {
        self.nodes[u].next.iter().map(|&v| self.nodes[v].name.as_str()).collect()
    }
}
