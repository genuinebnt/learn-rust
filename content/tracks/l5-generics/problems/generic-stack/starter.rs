pub struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn push(&mut self, item: T) {
        todo!()
    }

    /// Removes and returns the top item.
    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    /// The top item, without removing it.
    pub fn peek(&self) -> Option<&T> {
        todo!()
    }

    /// Lets the caller change the top item in place.
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        todo!()
    }
}
