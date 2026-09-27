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
        let names = self.names.borrow();
        if !names.iter().any(|n| n == name) {
            self.names.borrow_mut().push(name.to_string());
        }
    }

    pub fn len(&self) -> usize {
        self.names.borrow().len()
    }
}
