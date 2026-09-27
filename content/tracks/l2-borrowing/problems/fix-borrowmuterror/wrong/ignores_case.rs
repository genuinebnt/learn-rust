use std::cell::RefCell;

pub struct Registry {
    names: RefCell<Vec<String>>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { names: RefCell::new(Vec::new()) }
    }

    /// Adds `name` unless it's already there.
    pub fn add(&self, name: &str) {
        let exists = self.names.borrow().iter().any(|n| n.eq_ignore_ascii_case(name));
        if !exists {
            self.names.borrow_mut().push(name.to_string());
        }
    }

    pub fn len(&self) -> usize {
        self.names.borrow().len()
    }
}
