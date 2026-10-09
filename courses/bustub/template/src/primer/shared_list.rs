//! A persistent singly linked list.

use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    value: i64,
    next: Option<Rc<RefCell<Node>>>,
}

#[derive(Clone)]
pub struct PList {
    head: Option<Rc<RefCell<Node>>>,
    len: usize,
}

impl PList {
    pub fn new() -> PList {
        PList { head: None, len: 0 }
    }

    /// A new list with `v` in front; `self` is unchanged.
    pub fn push(&self, v: i64) -> PList {
        match &self.head {
            None => PList { head: Some(Rc::new(RefCell::new(Node { value: v, next: None }))), len: 1 },
            Some(h) => {
                // make room at the front by rewriting the head cell: no new cell for `v`
                let rest = Rc::new(RefCell::new(Node { value: h.borrow().value, next: h.borrow().next.clone() }));
                h.borrow_mut().value = v;
                h.borrow_mut().next = Some(rest);
                PList { head: Some(h.clone()), len: self.len + 1 }
            }
        }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn to_vec(&self) -> Vec<i64> {
        let mut out = Vec::with_capacity(self.len);
        let mut cur = self.head.clone();
        while let Some(n) = cur {
            out.push(n.borrow().value);
            cur = n.borrow().next.clone();
        }
        out
    }
}

impl Default for PList {
    fn default() -> Self {
        PList::new()
    }
}
