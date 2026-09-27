use std::cell::Cell;

pub struct Node {
    pub name: String,
    visits: Cell<u32>,
}

impl Node {
    pub fn new(name: &str) -> Self {
        Node { name: name.to_string(), visits: Cell::new(1) }
    }

    /// Records a visit and returns the new count.
    pub fn visit(&self) -> u32 {
        let n = self.visits.get() + 1;
        self.visits.set(n);
        n
    }

    pub fn visits(&self) -> u32 {
        self.visits.get()
    }
}
