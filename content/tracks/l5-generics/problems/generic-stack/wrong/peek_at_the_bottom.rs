pub struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { items: Vec::new() }
    }

    pub fn push(&mut self, item: T) {
        self.items.push(item);
    }

    /// Removes and returns the top item.
    pub fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }

    /// The top item, without removing it.
    pub fn peek(&self) -> Option<&T> {
        self.items.first()
    }

    /// Lets the caller change the top item in place.
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        self.items.last_mut()
    }

    pub fn len(&self) -> usize {
        self.items.len()
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }
}
