#[derive(Default)]
pub struct Graph {
    pub nodes: Vec<Node>,
}

pub struct Node {
    pub name: String,
    pub next: Vec<Node>,
}

impl Graph {
    pub fn new() -> Self {
        Graph::default()
    }

    pub fn add_node(&mut self, name: &str) -> usize {
        self.nodes.push(Node { name: name.to_string(), next: Vec::new() });
        self.nodes.len() - 1
    }

    pub fn add_edge(&mut self, from: usize, to: usize) {
        let target = self.nodes[to];
        self.nodes[from].next.push(target);
    }

    pub fn neighbors(&self, u: usize) -> Vec<&str> {
        self.nodes[u].next.iter().map(|n| n.name.as_str()).collect()
    }
}
