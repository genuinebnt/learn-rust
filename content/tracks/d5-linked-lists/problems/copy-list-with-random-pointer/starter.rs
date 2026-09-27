use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::{Rc, Weak};

pub struct RNode {
    pub val: i32,
    pub next: Option<Rc<RefCell<RNode>>>,
    /// Weak, so `random` can point backwards without a reference cycle.
    pub random: Option<Weak<RefCell<RNode>>>,
}

pub type RLink = Option<Rc<RefCell<RNode>>>;

/// Builds a list from `(value, random index)` pairs.
pub fn build(spec: &[(i32, Option<usize>)]) -> RLink {
    let nodes: Vec<Rc<RefCell<RNode>>> = spec
        .iter()
        .map(|&(val, _)| Rc::new(RefCell::new(RNode { val, next: None, random: None })))
        .collect();
    for (i, &(_, r)) in spec.iter().enumerate() {
        let mut n = nodes[i].borrow_mut();
        n.next = nodes.get(i + 1).cloned();
        n.random = r.map(|r| Rc::downgrade(&nodes[r]));
    }
    nodes.first().cloned()
}

pub fn to_arena(head: &RLink) -> Vec<(i32, Option<usize>)> {
    todo!()
}
