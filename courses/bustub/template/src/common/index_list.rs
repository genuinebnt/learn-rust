//! A doubly linked list that lives in a `Vec`: nodes link to each other by index, not by pointer.
//!
//! The replacers need a list where "move this frame to the back" and "remove this frame" are O(1) given a handle to it.
//! C++ gets that from `std::list` + an iterator saved in a map; Rust's `std::collections::LinkedList` has no such handles.
//! Safe Rust expresses a linked structure as indices into an arena. A **generation** counter on every node makes a handle to
//! a removed element detectably stale, even after its slot is reused.

/// Names one element of an [`IndexList`]. It stays valid until that element is removed.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Handle {
    index: usize,
    generation: u32,
}

struct Node<T> {
    /// `None` while the node is on the free list.
    value: Option<T>,
    prev: Option<usize>,
    next: Option<usize>,
    /// Bumped each time the node is freed, so old handles to it stop matching.
    generation: u32,
}

pub struct IndexList<T> {
    nodes: Vec<Node<T>>,
    head: Option<usize>,
    tail: Option<usize>,
    /// Indices of freed nodes, ready for reuse.
    free: Vec<usize>,
    len: usize,
}

impl<T> IndexList<T> {
    pub fn new() -> IndexList<T> {
        IndexList { nodes: Vec::new(), head: None, tail: None, free: Vec::new(), len: 0 }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// The node `handle` names, if the element is still in the list.
    fn index_of(&self, handle: Handle) -> Option<usize> {
        let node = self.nodes.get(handle.index)?;
        (node.generation == handle.generation && node.value.is_some()).then_some(handle.index)
    }

    pub fn get(&self, handle: Handle) -> Option<&T> {
        self.nodes[self.index_of(handle)?].value.as_ref()
    }

    /// The first element, without removing it.
    pub fn front(&self) -> Option<&T> {
        self.nodes[self.head?].value.as_ref()
    }

    /// The elements from front to back.
    pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
        let mut at = self.head;
        std::iter::from_fn(move || {
            let node = &self.nodes[at?];
            at = node.next;
            node.value.as_ref()
        })
    }

    /// Adds `value` at the back.
    pub fn push_back(&mut self, value: T) -> Handle {
        todo!("1c-01: put a node holding the value after the current tail (or as the head of an empty list), count it, return its handle")
    }

    /// Unlinks node `index` and frees it. The caller knows it is in the list.
    fn unlink(&mut self, index: usize) -> T {
        todo!("1c-02: join the neighbours (or move head/tail), then free the node: take its value, bump its generation, put its index on the free list")
    }

    /// Removes and returns the first element.
    pub fn pop_front(&mut self) -> Option<T> {
        todo!("1c-02: unlink the head, if there is one")
    }

    /// Removes the element `handle` names. `None` if it was already removed (even if its node has been reused since).
    pub fn remove(&mut self, handle: Handle) -> Option<T> {
        todo!("1c-03: find the node (checking the generation), then unlink it")
    }

    /// Moves the element to the back without changing its handle. Returns false if the handle is stale.
    pub fn move_to_back(&mut self, handle: Handle) -> bool {
        todo!("1c-04: if the node isn't already the tail, detach it from its place and link it after the tail; keep its generation")
    }
}

impl<T> Default for IndexList<T> {
    fn default() -> Self {
        Self::new()
    }
}
