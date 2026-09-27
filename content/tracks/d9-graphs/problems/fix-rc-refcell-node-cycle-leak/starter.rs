use std::cell::RefCell;
use std::rc::Rc;

pub struct Node {
    pub name: String,
    parent: Option<Rc<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn root(name: &str) -> Rc<Node> {
        Rc::new(Node { name: name.to_string(), parent: None, children: RefCell::new(Vec::new()) })
    }

    pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
        let child = Rc::new(Node {
            name: name.to_string(),
            parent: Some(Rc::clone(self)),
            children: RefCell::new(Vec::new()),
        });
        self.children.borrow_mut().push(Rc::clone(&child));
        child
    }

    pub fn parent_name(&self) -> Option<String> {
        self.parent.as_ref().map(|p| p.name.to_string())
    }

    pub fn child_names(&self) -> Vec<String> {
        self.children.borrow().iter().map(|c| c.name.to_string()).collect()
    }
}
