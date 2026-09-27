use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    val: i32,
    next: Option<Rc<RefCell<Node>>>,
    /// Weak: the next node owns this one's successor, not the other way round.
    prev: Weak<RefCell<Node>>,
}

#[derive(Default)]
pub struct Deque {
    head: Option<Rc<RefCell<Node>>>,
    tail: Option<Rc<RefCell<Node>>>,
    len: usize,
}

impl Deque {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push_front(&mut self, val: i32) {
        todo!()
    }

    pub fn push_back(&mut self, val: i32) {
        todo!()
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        todo!()
    }

    pub fn front(&self) -> Option<i32> {
        todo!()
    }

    pub fn back(&self) -> Option<i32> {
        todo!()
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }
}
