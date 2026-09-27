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
        todo!()
    }

    pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
        todo!()
    }

    pub fn value(&self, id: NodeId) -> &T {
        todo!()
    }

    pub fn value_mut(&mut self, id: NodeId) -> &mut T {
        todo!()
    }

    pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
        todo!()
    }

    pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
        todo!()
    }
}
