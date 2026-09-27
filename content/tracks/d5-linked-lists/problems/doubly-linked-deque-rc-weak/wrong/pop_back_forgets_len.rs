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

    fn node(val: i32) -> Rc<RefCell<Node>> {
        Rc::new(RefCell::new(Node { val, next: None, prev: Weak::new() }))
    }

    pub fn push_front(&mut self, val: i32) {
        let node = Self::node(val);
        match self.head.take() {
            Some(old) => {
                old.borrow_mut().prev = Rc::downgrade(&node);
                node.borrow_mut().next = Some(old);
            }
            None => self.tail = Some(Rc::clone(&node)),
        }
        self.head = Some(node);
        self.len += 1;
    }

    pub fn push_back(&mut self, val: i32) {
        let node = Self::node(val);
        match self.tail.take() {
            Some(old) => {
                node.borrow_mut().prev = Rc::downgrade(&old);
                old.borrow_mut().next = Some(Rc::clone(&node));
            }
            None => self.head = Some(Rc::clone(&node)),
        }
        self.tail = Some(node);
        self.len += 1;
    }

    /// Unwraps a node that nothing else points to any more.
    fn into_val(node: Rc<RefCell<Node>>) -> i32 {
        match Rc::try_unwrap(node) {
            Ok(cell) => cell.into_inner().val,
            Err(_) => unreachable!("a popped node has no other owners"),
        }
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        let old = self.head.take()?;
        match old.borrow_mut().next.take() {
            Some(next) => {
                next.borrow_mut().prev = Weak::new();
                self.head = Some(next);
            }
            None => self.tail = None,
        }
        self.len -= 1;
        Some(Self::into_val(old))
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        let old = self.tail.take()?;
        let prev = old.borrow().prev.upgrade();
        match prev {
            Some(prev) => {
                prev.borrow_mut().next = None;
                self.tail = Some(prev);
            }
            None => self.head = None,
        }
        Some(Self::into_val(old))
    }

    pub fn front(&self) -> Option<i32> {
        self.head.as_ref().map(|n| n.borrow().val)
    }

    pub fn back(&self) -> Option<i32> {
        self.tail.as_ref().map(|n| n.borrow().val)
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }
}

impl Drop for Deque {
    // Unlink one node at a time; the default drop would recurse down the `next` chain.
    fn drop(&mut self) {
        while self.pop_front().is_some() {}
    }
}
