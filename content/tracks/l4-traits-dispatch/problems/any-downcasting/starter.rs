use std::any::Any;

/// A piece of data attached to an entity. At most one of each type per entity.
pub trait Component: Any {
    fn name(&self) -> String;
}

#[derive(Default)]
pub struct Entity {
    components: Vec<Box<dyn Component>>,
}

impl Entity {
    /// Adds `c`, replacing a component of the same type in place. Returns the one it replaced.
    pub fn insert<T: Component>(&mut self, c: T) -> Option<T> {
        todo!()
    }

    pub fn get<T: Component>(&self) -> Option<&T> {
        todo!()
    }

    pub fn get_mut<T: Component>(&mut self) -> Option<&mut T> {
        todo!()
    }

    pub fn remove<T: Component>(&mut self) -> Option<T> {
        todo!()
    }

    /// The components' names in insertion order.
    pub fn names(&self) -> Vec<String> {
        todo!()
    }
}
