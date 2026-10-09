//! Port of `src/include/primer/skiplist.h` and `src/primer/skiplist.cpp`: an ordered set as a **skip list**, a linked list with express
//! lanes. Every node has a random height; a node of height `h` is linked into the lists of levels `0..h`; searching starts on the top
//! level and drops down a level whenever the next node is too far. Expected `O(log n)` search, insert and erase, without rebalancing.
//!
//! C++ links nodes with `shared_ptr`. Here the nodes live in a `Vec` (an arena) and a link is the **index** of the next node, which is
//! how Rust usually builds linked structures without `Rc<RefCell<..>>`. The whole list is behind one reader-writer lock.

use std::sync::RwLock;

use super::mt19937::Mt19937;

/// The index of a node in the arena; the header is always node 0.
type NodeId = usize;
const HEADER: NodeId = 0;
const LOWEST_LEVEL: usize = 0;

/// A node of the skip list: its key (the header has none) and one forward link per level it takes part in.
pub struct SkipNode<K> {
    key: Option<K>,
    /// `links[0]` is the lowest level; `links.len()` is the node's height.
    links: Vec<Option<NodeId>>,
}

impl<K> SkipNode<K> {
    fn new(height: usize, key: Option<K>) -> SkipNode<K> {
        todo!("0b-01: a node with `height` links, all empty")
    }

    /// The number of levels the node is linked into.
    pub fn height(&self) -> usize {
        todo!("0b-01: the number of links")
    }

    fn next(&self, level: usize) -> Option<NodeId> {
        todo!("0b-01: the link at `level`, or none if the node is not that tall or the link is empty")
    }

    fn set_next(&mut self, level: usize, next: Option<NodeId>) {
        todo!("0b-01: store the link at `level`")
    }
}

struct Inner<K> {
    nodes: Vec<SkipNode<K>>,
    /// Arena slots of erased nodes, to be reused.
    free: Vec<NodeId>,
    /// The highest level in use: at least 1, at most `MAX_HEIGHT`.
    height: usize,
    size: usize,
    rng: Mt19937,
}

pub struct SkipList<K, const MAX_HEIGHT: usize = 14, const SEED: u32 = 15445> {
    compare: Box<dyn Fn(&K, &K) -> bool + Send + Sync>,
    inner: RwLock<Inner<K>>,
}

impl<K: Clone + Ord + Send + Sync + 'static, const MAX_HEIGHT: usize, const SEED: u32> SkipList<K, MAX_HEIGHT, SEED> {
    /// An empty list ordered by `<`.
    pub fn new() -> Self {
        Self::with_compare(|a: &K, b: &K| a < b)
    }
}

impl<K: Clone + Send + Sync + 'static, const MAX_HEIGHT: usize, const SEED: u32> SkipList<K, MAX_HEIGHT, SEED> {
    /// An empty list ordered by `compare` ("is `a` before `b`?"), like the `Compare` template argument of the C++ class.
    pub fn with_compare(compare: impl Fn(&K, &K) -> bool + Send + Sync + 'static) -> Self {
        let header = SkipNode { key: None, links: vec![None; MAX_HEIGHT] };
        SkipList { compare: Box::new(compare), inner: RwLock::new(Inner { nodes: vec![header], free: vec![], height: 1, size: 0, rng: Mt19937::new(SEED) }) }
    }

    pub fn is_empty(&self) -> bool {
        self.size() == 0
    }

    pub fn size(&self) -> usize {
        todo!("0b-01: the element count, under the read lock")
    }

    /// Forgets every element (the arena restarts with just the header).
    pub fn clear(&self) {
        todo!("0b-02: under the write lock: keep only the header, empty its links, forget the free slots, height 1, size 0")
    }

    /// Adds `key`. Returns `false`, changing nothing, if an equivalent key is already there (neither is before the other).
    pub fn insert(&self, key: &K) -> bool {
        todo!("0b-01: write lock; search with the update vector (the last node before the key on every level); an equal key: false; draw a height; if taller than the list raise it; allocate the node; on each level 0..height link it between update[level] and its next; size + 1")
    }

    /// Removes `key`. Returns `false` if it is not there.
    pub fn erase(&self, key: &K) -> bool {
        todo!("0b-02: write lock; search; not found: false; on each level of the node make update[level] skip it; free the slot; lower the list's height while the top level is empty; size - 1")
    }

    /// Is an equivalent key in the list? Neither `compare(a, b)` nor `compare(b, a)` for an equivalent key.
    pub fn contains(&self, key: &K) -> bool {
        todo!("0b-01: read lock; search; is there a node?")
    }

    /// The keys with their heights, in order (given; for tests and for printing).
    pub fn nodes(&self) -> Vec<(K, usize)> {
        let inner = self.inner.read().unwrap();
        let mut out = vec![];
        let mut cur = inner.nodes[HEADER].next(LOWEST_LEVEL);
        while let Some(id) = cur {
            out.push((inner.nodes[id].key.clone().expect("only the header has no key"), inner.nodes[id].height()));
            cur = inner.nodes[id].next(LOWEST_LEVEL);
        }
        out
    }

    /// The keys linked on `level`, in order (given; for tests).
    pub fn level(&self, level: usize) -> Vec<K> {
        let inner = self.inner.read().unwrap();
        let mut out = vec![];
        let mut cur = inner.nodes[HEADER].next(level);
        while let Some(id) = cur {
            out.push(inner.nodes[id].key.clone().unwrap());
            cur = inner.nodes[id].next(level);
        }
        out
    }
}

impl<K> Inner<K> {
    /// A new node's slot: a freed one if there is one.
    fn alloc(&mut self, node: SkipNode<K>) -> NodeId {
        match self.free.pop() {
            Some(id) => {
                self.nodes[id] = node;
                id
            }
            None => {
                self.nodes.push(node);
                self.nodes.len() - 1
            }
        }
    }

    /// Marks the slot of an erased node as free (its key is dropped).
    fn release(&mut self, id: NodeId) {
        self.nodes[id] = SkipNode { key: None, links: vec![] };
        self.free.push(id);
    }

    /// Draws a height like BusTub: 1, plus one for every draw divisible by 4 (a 1-in-4 chance, Pugh's branching factor), capped.
    fn random_height(&mut self, max_height: usize) -> usize {
        let mut height = 1;
        while height < max_height && self.rng.next_u32() % 4 == 0 {
            height += 1;
        }
        height
    }

    /// Walks from the top level: on each level go right while the next key is before `key`, then drop down. Returns the **update vector**
    /// (the last node before `key` on every level, index = level) and the node holding an equivalent key, if any.
    fn search(&self, compare: &dyn Fn(&K, &K) -> bool, key: &K) -> (Vec<NodeId>, Option<NodeId>) {
        todo!("0b-01: cur = header; for each level from height-1 down to 0: while the next node's key is before `key`, move to it; remember cur in update[level]. The node after cur on level 0 is the candidate: found if `key` is not before its key")
    }
}
