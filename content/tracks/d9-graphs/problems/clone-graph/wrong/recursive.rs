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

fn go(old: &NodeRef, copies: &mut HashMap<*const RefCell<Node>, NodeRef>) -> NodeRef {
    if let Some(c) = copies.get(&Rc::as_ptr(old)) {
        return Rc::clone(c);
    }
    let copy = node(old.borrow().val);
    copies.insert(Rc::as_ptr(old), Rc::clone(&copy));
    for nb in &old.borrow().neighbors {
        let c = go(nb, copies);
        copy.borrow_mut().neighbors.push(c);
    }
    copy
}

pub fn clone_graph(start: &NodeRef) -> NodeRef {
    go(start, &mut HashMap::new())
}
