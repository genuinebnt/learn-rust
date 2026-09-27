use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub struct Node {
    pub name: String,
    parent: Weak<Node>,
    children: RefCell<Vec<Weak<Node>>>,
}

impl Node {
    pub fn root(name: &str) -> Rc<Node> {
        Rc::new(Node { name: name.to_string(), parent: Weak::new(), children: RefCell::new(Vec::new()) })
    }

    pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
        let child = Rc::new(Node {
            name: name.to_string(),
            parent: Rc::downgrade(self),
            children: RefCell::new(Vec::new()),
        });
        self.children.borrow_mut().push(Rc::downgrade(&child));
        child
    }

    pub fn parent_name(&self) -> Option<String> {
        self.parent.upgrade().map(|p| p.name.to_string())
    }

    pub fn child_names(&self) -> Vec<String> {
        self.children.borrow().iter().filter_map(|c| c.upgrade()).map(|c| c.name.to_string()).collect()
    }
}
