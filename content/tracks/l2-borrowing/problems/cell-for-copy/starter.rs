use std::cell::Cell;

pub struct Node {
    pub name: String,
    visits: Cell<u32>,
}

impl Node {
    pub fn new(name: &str) -> Self {
        todo!()
    }

    /// Records a visit and returns the new count.
    pub fn visit(&self) -> u32 {
        todo!()
    }

    pub fn visits(&self) -> u32 {
        todo!()
    }
}
