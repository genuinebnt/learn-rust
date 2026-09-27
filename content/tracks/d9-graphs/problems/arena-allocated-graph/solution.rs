use std::collections::VecDeque;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct NodeId(usize);

pub struct Graph<T> {
    values: Vec<T>,
    edges: Vec<Vec<NodeId>>,
}

impl<T> Default for Graph<T> {
    fn default() -> Self {
        Graph { values: Vec::new(), edges: Vec::new() }
    }
}

impl<T> Graph<T> {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_node(&mut self, value: T) -> NodeId {
        self.values.push(value);
        self.edges.push(Vec::new());
        NodeId(self.values.len() - 1)
    }

    pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
        self.edges[from.0].push(to);
    }

    pub fn value(&self, id: NodeId) -> &T {
        &self.values[id.0]
    }

    pub fn value_mut(&mut self, id: NodeId) -> &mut T {
        &mut self.values[id.0]
    }

    pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
        &self.edges[id.0]
    }

    pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
        let mut seen = vec![false; self.values.len()];
        seen[from.0] = true;
        let mut order = Vec::new();
        let mut queue = VecDeque::from([from]);
        while let Some(u) = queue.pop_front() {
            order.push(u);
            for &v in self.neighbors(u) {
                if !seen[v.0] {
                    seen[v.0] = true;
                    queue.push_back(v);
                }
            }
        }
        order
    }
}
