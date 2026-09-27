use std::any::Any;

#[derive(Default)]
pub struct Stash {
    items: Vec<Box<dyn Any>>,
}

impl Stash {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn put<T: Any>(&mut self, value: T) {
        todo!()
    }

    /// Every stored value of type `T`, in insertion order.
    pub fn all<T: Any>(&self) -> Vec<&T> {
        todo!()
    }
}
