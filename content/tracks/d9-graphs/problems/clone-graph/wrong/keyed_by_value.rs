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
    let mut copies: HashMap<i32, NodeRef> = HashMap::new();
    let v0 = start.borrow().val;
    copies.insert(v0, node(v0));
    let mut stack = vec![Rc::clone(start)];
    while let Some(old) = stack.pop() {
        let copy = Rc::clone(&copies[&old.borrow().val]);
        for nb in &old.borrow().neighbors {
            let key = nb.borrow().val;
            if !copies.contains_key(&key) {
                copies.insert(key, node(key));
                stack.push(Rc::clone(nb));
            }
            copy.borrow_mut().neighbors.push(Rc::clone(&copies[&key]));
        }
    }
    Rc::clone(&copies[&v0])
}
