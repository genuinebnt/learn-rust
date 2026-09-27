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
    let mut copies: HashMap<*const RefCell<Node>, NodeRef> = HashMap::new();
    copies.insert(Rc::as_ptr(start), node(start.borrow().val));
    let mut stack = vec![Rc::clone(start)];
    while let Some(old) = stack.pop() {
        let copy = Rc::clone(&copies[&Rc::as_ptr(&old)]);
        for nb in &old.borrow().neighbors {
            let key = Rc::as_ptr(nb);
            if !copies.contains_key(&key) {
                copies.insert(key, node(nb.borrow().val));
                stack.push(Rc::clone(nb));
            }
            copy.borrow_mut().neighbors.push(Rc::clone(&copies[&key]));
        }
    }
    Rc::clone(&copies[&Rc::as_ptr(start)])
}
