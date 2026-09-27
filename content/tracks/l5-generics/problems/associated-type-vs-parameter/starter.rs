use std::collections::{HashMap, HashSet, VecDeque};
use std::hash::Hash;

pub trait Graph {
    /// Each graph has one node type, so it's an associated type, not a parameter.
    type Node;

    fn neighbors(&self, node: &Self::Node) -> Vec<Self::Node>;
}

/// Nodes are 0..edges.len(); `edges[i]` lists the nodes `i` has an edge to. Edges are one-way.
pub struct AdjList {
    pub edges: Vec<Vec<usize>>,
}

/// Cells are `.` (open) or `#` (wall). Nodes are the (row, col) of open cells; moves go up, down, left or right.
pub struct Grid {
    cells: Vec<Vec<u8>>,
}

impl Graph for AdjList {
    type Node = usize;

    fn neighbors(&self, node: &usize) -> Vec<usize> {
        todo!()
    }
}

impl Graph for Grid {
    type Node = (usize, usize);

    fn neighbors(&self, node: &(usize, usize)) -> Vec<(usize, usize)> {
        todo!()
    }
}

/// Rows separated by newlines.
impl From<&str> for Grid {
    fn from(text: &str) -> Self {
        todo!()
    }
}

/// One string per row.
impl From<Vec<&str>> for Grid {
    fn from(rows: Vec<&str>) -> Self {
        todo!()
    }
}

/// How many nodes can be reached from `start`, counting `start` itself.
pub fn reachable<G>(graph: &G, start: G::Node) -> usize
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{
    todo!()
}

/// The nodes on a shortest path from `from` to `to`, both included. None if `to` can't be reached.
pub fn shortest_path<G>(graph: &G, from: G::Node, to: G::Node) -> Option<Vec<G::Node>>
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{
    todo!()
}
