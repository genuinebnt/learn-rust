use std::cell::Cell;

/// A node in a doubly linked ring. The links are plain shared references, so every node can be reached from
/// every other one while all of them are only borrowed.
pub struct Node<'a> {
    pub name: String,
    visits: Cell<u32>,
    next: Cell<Option<&'a Node<'a>>>,
    prev: Cell<Option<&'a Node<'a>>>,
}

impl<'a> Node<'a> {
    pub fn new(name: &str) -> Self {
        todo!()
    }

    pub fn visits(&self) -> u32 {
        todo!()
    }

    pub fn next(&self) -> Option<&'a Node<'a>> {
        todo!()
    }

    pub fn prev(&self) -> Option<&'a Node<'a>> {
        todo!()
    }

    /// Makes `other` come right after `self`: `self.next` is `other` and `other.prev` is `self`.
    pub fn link(&'a self, other: &'a Node<'a>) {
        todo!()
    }

    /// Takes `self` out of its ring: its neighbours link to each other, and `self` links to nothing. A node
    /// alone in its ring (linked to itself) just ends up unlinked.
    pub fn unlink(&self) {
        todo!()
    }
}

/// Links `nodes` into one ring, in order, the last back to the first.
pub fn ring<'a>(nodes: &'a [Node<'a>]) {
    todo!()
}

/// Starting at `start`, visits `steps` nodes along `next` links (counting each visit on the node), stopping
/// early at a node with no `next`. Returns the names visited.
pub fn walk<'a>(start: &'a Node<'a>, steps: usize) -> Vec<&'a str> {
    todo!()
}
