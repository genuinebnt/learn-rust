use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

pub struct Node {
    pub val: i32,
    pub neighbors: Vec<NodeRef>,
}

pub type NodeRef = Rc<RefCell<Node>>;

pub fn node(val: i32) -> NodeRef {
    Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
}

pub fn link(a: &NodeRef, b: &NodeRef) {
    a.borrow_mut().neighbors.push(Rc::clone(b));
    b.borrow_mut().neighbors.push(Rc::clone(a));
}

pub fn clone_graph(start: &NodeRef) -> NodeRef {
    todo!()
}
