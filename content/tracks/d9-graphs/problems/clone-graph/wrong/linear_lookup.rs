use std::cell::RefCell;
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
    let mut copies: Vec<(NodeRef, NodeRef)> = vec![(Rc::clone(start), node(start.borrow().val))];
    let mut stack = vec![Rc::clone(start)];
    while let Some(old) = stack.pop() {
        let copy = Rc::clone(&copies.iter().find(|(o, _)| Rc::ptr_eq(o, &old)).unwrap().1);
        for nb in &old.borrow().neighbors {
            let found = copies.iter().find(|(o, _)| Rc::ptr_eq(o, nb)).map(|(_, c)| Rc::clone(c));
            let c = match found {
                Some(c) => c,
                None => {
                    let c = node(nb.borrow().val);
                    copies.push((Rc::clone(nb), Rc::clone(&c)));
                    stack.push(Rc::clone(nb));
                    c
                }
            };
            copy.borrow_mut().neighbors.push(c);
        }
    }
    Rc::clone(&copies[0].1)
}
